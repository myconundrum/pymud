NAME_ATTR 		= 'name'
DESC_ATTR 		= 'desc'
DROPTO_ATTR 	= 'dropto'
OSUCCESS_ATTR   = 'osuccess'

ROOM_FLAG 		= 'ROOM'
EXIT_FLAG 		= 'EXIT'
PLAYER_FLAG 	= 'PLAYER'
OPAQUE_FLAG		= 'OPAQUE'
HIDDEN_FLAG     = 'HIDDEN'



_commands = {}
_nospacecommands = {}

_master_room = 1


NO_DESC_MESSAGE = 'You see nothing special.'

from db import *
from world import get_world
from player import * 


def _get_room_inventory(loc,hidden) :
	db = get_db()
	return [x for x in db.oget_contains(loc) if (not db.ohas_flag(x,EXIT_FLAG)) and (hidden or not db.ohas_flag(x,HIDDEN_FLAG))]
	
		
def _get_room_exits(loc,hidden) :
	db = get_db()
	return [x for x in db.oget_contains(loc) if db.ohas_flag(x,EXIT_FLAG) and (hidden or not db.ohas_flag(x,HIDDEN_FLAG))]
	

def _get_dbref(player,a):

	db = get_db()
	loc = db.oget_location(player.dbref)
	# get "built in references
	if a == 'here':
		return loc
	if a == 'me':
		return player.dbref 
	if a[0]=='#':
		return int(a[1:])

	# is this the name of an object the player is carrying?
	for l in db.oget_contains(player.dbref):
		if a == db.oget_attribute(l,NAME_ATTR):
			return l

	# is this the name of an object in the same room?
	for l in _get_room_inventory(loc,False):
		if a == db.oget_attribute(l,NAME_ATTR):
			return l 

	# is this an exit (including alias)
	for e in _get_room_exits(loc,False):
		if (_match_exit_alias(e,a)):
			return e

	return db.nothing


def _split_command_string_on(args,sp):
	a = args.split(sp,1)
	return [a[0].strip(),a[1].strip()] if len(a) == 2 else [args.strip(),None]


def _set_named_attr(player,args,extra):
	
	db = get_db()
	a = _split_command_string_on(args,'=')
	dbref = _get_dbref(player,a[0])

	if (dbref != db.nothing):
			db.oset_attribute(dbref,extra,a[1])
			player.send("Set.")
	else : 
		player.send("Invalid format for command." if a[1] == None else 'I don\'t see anything named ' + a[0] + ' here.')

def cmd_quit(player,args,extra):
	player.send("Goodbye.")
	player.logout()
	
def cmd_shutdown(player,args,extra):
	# should only be possible with special permissions.
	get_world().quit()


def _broadcast_location(dbref,msg):

	db = get_db()
	for p in get_player_manager().get_connected_players():
		if db.oget_location(p.dbref) == dbref:
			p.send(msg)



def cmd_emote(player,args,emoteformat):
	_broadcast_location(
		get_db().oget_location(player.dbref),
		get_db().oget_attribute(player.dbref,NAME_ATTR) + emoteformat.format(args))


def cmd_create(player,args,extra):

	db = get_db()
	# no quota or cost right now.
	if (args.strip() == ''):
		player.send("Create what?")
	else:
		o = db.ocreate()
		db.oset_attribute(o,NAME_ATTR,args)
		db.omove(o,player.dbref)


def cmd_look(player,args,extra):

	db = get_db()


	loc = db.oget_location(player.dbref)
	dbref = loc if args == '' else _get_dbref(player,args)
	if dbref == db.nothing:
		player.send('you don\'t see anything named ' + args +' here.')
		return

	player.send('['+db.oget_attribute(dbref,NAME_ATTR)+']')

	if (db.ohas_attribute(dbref,DESC_ATTR)):
		player.send(db.oget_attribute(dbref,DESC_ATTR))
	else :
		player.send(NO_DESC_MESSAGE)

	# room...
	if (dbref == loc) :
		contains = _get_room_inventory(dbref,False)
		exits = _get_room_exits(dbref,False)
		contains.remove(player.dbref)

		if (len(exits)>0):
			player.send('Exits:')
			for e in exits:
				player.send(db.oget_attribute(e,NAME_ATTR).split(';')[0])

		if (len(contains)>0):
			player.send("You see:")
			for l in contains: 
				player.send(db.oget_attribute(l,NAME_ATTR))
	else:
		if (not db.ohas_flag(dbref,OPAQUE_FLAG)):
			contains = db.oget_contains(dbref)

			if (len(contains)>0):
				player.send('Carrying:')
				for l in contains: 
					player.send(db.oget_attribute(l,NAME_ATTR))
	
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
	
 
def cmd_dig(player,args,extra):

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

	

def _command_move_player(player,loc):
	get_db().omove(player.dbref,loc)
	cmd_look(player,'',None)
	

def cmd_dump(player,args,extra):
	get_world().save("in.db")
	

def cmd_teleport(player,args,extra):

	db = get_db()
	a = _split_command_string_on(args,'=')
	loc = _get_dbref(player,a[0]) if a[1] == None else _get_dbref(player,a[1])
	dbref = player.dbref if a[1] == None else _get_dbref(player,a[0])
	
	if db.ohas_flag(loc,ROOM_FLAG) and not db.ohas_flag(dbref,ROOM_FLAG) and not db.ohas_flag(dbref,EXIT_FLAG):
		db.omove(dbref,loc)
		cmd_look(player,'',None)


def init_commands() : 
	_commands['look'] 			= [cmd_look,None]
	_commands['l'] 				= [cmd_look,None]
	_commands['quit']   		= [cmd_quit,None]
	_commands['logout'] 		= [cmd_quit,None]
	_commands['shutdown']       = [cmd_shutdown,None]
	_commands['say'] 			= [cmd_emote,' says, "{}"']
	_commands['pose'] 			= [cmd_emote,' {}']
	_commands['semipose']		= [cmd_emote,'{}']
	_nospacecommands[':'] 		= [cmd_emote,' {}']
	_nospacecommands[';'] 		= [cmd_emote,'{}']
	_nospacecommands['"']       = [cmd_emote,' says, "{}"']
	_commands['@name']			= [_set_named_attr,NAME_ATTR] 
	_commands['@create']		= [cmd_create,None]
	_commands['@describe']		= [_set_named_attr,DESC_ATTR]
	_commands['@desc'] 			= [_set_named_attr,DESC_ATTR]
	_commands['@dig'] 			= [cmd_dig,None]
	_commands['@teleport'] 		= [cmd_teleport,None] 
	_commands['@tel']			= [cmd_teleport,None]
	_commands['@osucc']			= [_set_named_attr,OSUCCESS_ATTR]
	_commands['@osuccess']		= [_set_named_attr,OSUCCESS_ATTR]

	#_commadns['@dig/teleport']  = cmd_dig_teleport


def _match_exit_alias(e,str) :
	for n in get_db().oget_attribute(e,NAME_ATTR).split(';'):
		if n==str:
			return True
	return False

def cmd_take_exit(player,exit):

	db = get_db()
	if not db.ohas_attribute(exit,DROPTO_ATTR):
		player.send('That exit leads nowhere...[unlinked exit]')
		return

	if db.ohas_attribute(exit,OSUCCESS_ATTR):
		_broadcast_location(db.oget_location(player.dbref),db.oget_attribute(exit,OSUCCESS_ATTR))

	_command_move_player(player,db.oget_attribute(exit,DROPTO_ATTR))


def hide_player(player_dbref):
	get_db().oset_flag(player_dbref,HIDDEN_FLAG)

def unhide_player(player_dbref):
	if (get_db().ohas_flag(player_dbref,HIDDEN_FLAG)):
		get_db().oclear_flag(player_dbref,HIDDEN_FLAG)

def connect_character(player,name,password):
	
	dbref = get_player_manager().connect_player(name,password)

	if dbref == -1 :
		player.send("Invalid character name or password.")

	player.dbref = dbref
	player.set_connecting(False)
	player.send("Connected...\n")
	unhide_player(player.dbref)
	cmd_look(player,'',None)


def create_character(player,name,password):
	
	dbref = get_player_manager().create_player(name,password)

	if (dbref == -1): 
		player.send("That name already exists.")
		return 
	
	player.dbref = dbref 
	# move past login..
	player.set_connecting(False)

	db = get_db()

	db.oset_attribute(dbref,NAME_ATTR,name)
	db.oset_flag(dbref,PLAYER_FLAG)
	db.omove(dbref,_master_room)

	player.send("Character named " + name + " created.")

	cmd_look(player,'',None)


def process_connecting(player,args):
	args = args.split(' ')
	if (args[0] == 'create') and (len(args) == 3):
		create_character(player,args[1],args[2])
	elif (args[0] == 'connect' and len(args) == 3):
		connect_character(player,args[1],args[2])
	else:
		player.send("Only connect or create allowed here.")

def process_command(player,args) :

	# while connecting, players have access to fewer commands.
	if (player.is_connecting()):
		process_connecting(player,args)
		return


	matched = False

	if (len(args)==0) :
		return

	w = get_world() 
	db = get_db()

	for e in _get_room_exits(db.oget_location(player.dbref),True):
		if (_match_exit_alias(e,args)):
			cmd_take_exit(player,e)
			matched = True

	# test 1 character / nospace commands
	if (not matched) and (args[0] in _nospacecommands):
		_nospacecommands[args[0]][0](player,args[1:],_nospacecommands[args[0]][1])
		matched = True

	if not matched:
		# test regular commands
		args = args.split(' ',1)
		if args[0] in _commands : 
			if len(args) == 1:
				args.append('')
			_commands[args[0]][0](player,args[1],_commands[args[0]][1])
			matched = True

	if not matched: 
		player.send("huh?")






