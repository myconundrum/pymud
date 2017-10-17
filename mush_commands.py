NAME_ATTR 		= 'name'
DESC_ATTR 		= 'desc'
DROPTO_ATTR 	= 'dropto'


ROOM_FLAG 		= 'ROOM'
EXIT_FLAG 		= 'EXIT'
PLAYER_FLAG 	= 'PLAYER'
OPAQUE_FLAG		= 'OPAQUE'

_commands = {}
_nospacecommands = {}

_master_room = 1


NO_DESC_MESSAGE = 'You see nothing special.'

from db import *
from world import get_world
from player import * 


def _get_room_inventory(w,loc) :
	db = get_db()
	return [x for x in db.oget_contains(loc) if not db.ohas_flag(x,EXIT_FLAG)]

def _get_room_exits(w,loc) :
	db = get_db()
	return [x for x in db.oget_contains(loc) if db.ohas_flag(x,EXIT_FLAG)]

def _get_dbref(player,a):

	db = get_db()
	# get "built in references
	if a == 'here':
		return db.oget_location(player.dbref)
	if a == 'me':
		return player.dbref 
	if a[0]=='#':
		return int(a[1:])

	# is this the name of an object the player is carrying?
	for l in db.oget_contains(player.dbref):
		if a == db.oget_attribute(l,NAME_ATTR):
			return l

	# is this the name of an object in the same room?
	for l in db.oget_contains(db.oget_location(player.dbref)):
		if a == db.oget_attribute(l,NAME_ATTR):
			return l 

	return db.nothing


def _split_command_string_on(args,sp):
	a = args.split(sp,1)
	return [a[0].strip(),a[1].strip()] if len(a) == 2 else [args.strip(),None]

def cmd_name(player,args):

	db = get_db()
	rmsg = ''
	a = _split_command_string_on(args,'=')
	dbref = _get_dbref(player,a[0])

	if (dbref != db.nothing):
		db.oset_attribute(dbref,NAME_ATTR,a[1])
		rmsg = 'Named.'
	else : 
		rmsg = 'Invalid format for @name command.' if a[1] == None else 'I don\'t see anything named ' + a[0] + ' here.'
	return rmsg

def cmd_quit(player,args):
	get_world().quit()
	return ''

def cmd_pose(player,args):
	return get_db().oget_attribute(player.dbref,NAME_ATTR) + ' ' + args

def cmd_semipose(player,args):
	return get_db().oget_attribute(player.dbref,NAME_ATTR) + args

def cmd_say(player,args):
	return get_db().oget_attribute(player.dbref,NAME_ATTR) + ' says, "'+args+'"'

def cmd_create(player,args):

	db = get_db()
	# no quota or cost right now.
	if (args.strip() == ''):
		return "Create what?"
	else:
		o = db.ocreate()
		db.oset_attribute(o,NAME_ATTR,args)
		db.omove(o,player.dbref)
	return ''

def cmd_describe(player,args):
	
	db = get_db()
	rmsg = ''
	a = _split_command_string_on(args,'=')
	dbref = _get_dbref(player,a[0])

	if (dbref != db.nothing):
		if (a[1] != None):
			db.oset_attribute(dbref,DESC_ATTR,a[1])
			rmsg = 'Described.'
		else :
			db.oclear_attribute(dbref,DESC_ATTR)
	else : 
		rmsg = 'I don\'t see anything named ' + a[0] + ' here.'

	return rmsg
			


def cmd_look(player,args):

	rmsg = ''
	db = get_db()


	loc = db.oget_location(player.dbref)
	dbref = loc if args == '' else _get_dbref(player,args)
	if dbref == db.nothing:
		return 'you don\'t see anything named ' + args +' here.'

	rmsg = db.oget_attribute(dbref,NAME_ATTR) + '\n'
	if (db.ohas_attribute(dbref,DESC_ATTR)):
		rmsg = rmsg +  db.oget_attribute(dbref,DESC_ATTR)
	else :
		rmsg = rmsg + NO_DESC_MESSAGE

	# room...
	if (dbref == loc) :
		contains = _get_room_inventory(player,dbref)
		exits = _get_room_exits(player,dbref)
		contains.remove(player.dbref)

		if (len(exits)>0):
			rmsg = rmsg + '\nExits:'
			for e in exits:
				rmsg = rmsg + '\n'+ db.oget_attribute(e,NAME_ATTR).split(';')[0]

		if (len(contains)>0):
			rmsg = rmsg + '\n' + "You see:"
			for l in contains: 
				rmsg = rmsg + '\n' + db.oget_attribute(l,NAME_ATTR)
	else:
		if (not db.ohas_flag(dbref,OPAQUE_FLAG)):
			contains = db.oget_contains(dbref)

			if (len(contains)>0):
				rmsg = rmsg + '\nCarrying:'
				for l in contains: 
					rmsg = rmsg + '\n' + db.oget_attribute(l,NAME_ATTR)
	return rmsg

  #@dig <room name> [= <exit name>;<exit alias>*,<exit name>;<exit alias>*]
  #@dig/teleport


def _unlink_exit(player,exit):
	# should remove reference in linked room.. Currently unimplemented
	pass

def _link_exit(player,exit,todbref):
	db = get_db()
	if db.ohas_flag(exit,EXIT_FLAG) and db.ohas_flag(todbref,ROOM_FLAG):
		_unlink_exit(player,exit)
		db.oset_attribute(exit,DROPTO_ATTR,todbref)
	return ''
 
def cmd_dig(player,args):

	db = get_db()
	a = _split_command_string_on(args,'=')
	
	o = db.ocreate()
	db.oset_attribute(o,NAME_ATTR,a[0])
	db.oset_flag(o,ROOM_FLAG)

	if (a[1] != None):
		a = _split_command_string_on(a[1],',')
		e1 = db.ocreate()
		db.oset_attribute(e1,NAME_ATTR,a[0])
		db.oset_flag(e1,EXIT_FLAG)
		db.omove(e1,db.oget_location(player.dbref))
		_link_exit(player,e1,o)
		if (a[1] != None):
			e2 = db.ocreate()
			db.oset_attribute(e2,NAME_ATTR,a[1])
			db.oset_flag(e2,EXIT_FLAG)
			db.omove(e2,o)
			_link_exit(player,e2,db.oget_location(player.dbref))

	return ''
		

def _command_move_player(player,loc):
	get_db().omove(player.dbref,loc)
	return ''

def cmd_dump(player,args):
	get_world().save("in.db")
	return ''



def cmd_teleport(player,args):

	db = get_db()
	rmsg = ''
	a = _split_command_string_on(args,'=')
	loc = _get_dbref(player,a[0]) if a[1] == None else _get_dbref(player,a[1])
	dbref = player.dbref if a[1] == None else _get_dbref(player,a[0])
	
	if db.ohas_flag(loc,ROOM_FLAG) and not db.ohas_flag(dbref,ROOM_FLAG) and not db.ohas_flag(dbref,EXIT_FLAG):
		db.omove(dbref,loc)
		rmsg = cmd_look(player,'')


	return rmsg

def init_commands() : 
	_commands['look'] 			= cmd_look
	_commands['l'] 				= cmd_look
	_commands['quit']   		= cmd_quit
	_commands['say'] 			= cmd_say
	_commands['pose'] 			= cmd_pose
	_commands['semipose']		= cmd_semipose
	_nospacecommands[':'] 		= cmd_pose
	_nospacecommands[';'] 		= cmd_semipose
	_nospacecommands['"']       = cmd_say
	_commands['@name']			= cmd_name 
	_commands['@create']		= cmd_create
	_commands['@describe']		= cmd_describe
	_commands['@desc'] 			= cmd_describe
	_commands['@dig'] 			= cmd_dig
	_commands['@teleport'] 		= cmd_teleport 
	_commands['@tel']			= cmd_teleport 
	#_commadns['@dig/teleport']  = cmd_dig_teleport


def _match_exit_alias(e,str) :
	for n in get_db().oget_attribute(e,NAME_ATTR).split(';'):
		if n==str:
			return True
	return False


def connect_character(player,name,password):
	
	dbref = get_player_manager().connect_player(name,password)

	if dbref == -1 :
		return "Invalid character name or password."

	player.dbref = dbref
	player.set_connecting(False)
	return "Connected..."




def create_character(player,name,password):
	
	dbref = get_player_manager().create_player(name,password)

	if (dbref == -1): 
		return "That name already exists."
	
	player.dbref = dbref 
	# move past login..
	player.set_connecting(False)

	db = get_db()

	db.oset_attribute(dbref,NAME_ATTR,name)
	db.oset_flag(dbref,PLAYER_FLAG)
	db.omove(dbref,_master_room)

	return "Character named " + name + " created.\n" 

	cmd_look(player,'')


def process_connecting(player,args):
	args = args.split(' ')
	if (args[0] == 'create') and (len(args) == 3):
		return create_character(player,args[1],args[2])
	elif (args[0] == 'connect' and len(args) == 3):
		return connect_character(player,args[1],args[2])
	else:
		return "Only connect or create allowed here."



def process_command(player,args) :

	if (player.is_connecting()):
		return process_connecting(player,args)

	matched = False

	if (len(args)==0) :
		return ""
	w = get_world() 
	db = get_db()

	for e in _get_room_exits(player,db.oget_location(player.dbref)):
		if (_match_exit_alias(e,args)):
			rmsg = _command_move_player(player,db.oget_attribute(e,DROPTO_ATTR))
			matched = True

	# test 1 character / nospace commands
	if (not matched) and (args[0] in _nospacecommands):
		rmsg = _nospacecommands[args[0]](player,args[1:])
		matched = True

	if not matched:
		# test regular commands
		args = args.split(' ',1)
		if args[0] in _commands : 
			if len(args) == 1:
				args.append('')
			rmsg = _commands[args[0]](player,args[1])
			matched = True

	if not matched: 
		rmsg = 'huh?'

	return rmsg + '\n'


def do_commands(w) :

	args = input('> ')
	





