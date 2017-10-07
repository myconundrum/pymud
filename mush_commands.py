NAME_ATTR 		= 'name'
DESC_ATTR 		= 'desc'
DROPTO_ATTR 	= 'dropto'


ROOM_FLAG 		= 'ROOM'
EXIT_FLAG 		= 'EXIT'
PLAYER_FLAG 	= 'PLAYER'
OPAQUE_FLAG		= 'OPAQUE'

_commands = {}
_nospacecommands = {}


NO_DESC_MESSAGE = 'You see nothing special.'



def _get_room_inventory(w,loc) :
	return [x for x in w.db.oget_contains(loc) if not w.db.ohas_flag(x,EXIT_FLAG)]

def _get_room_exits(w,loc) :
	return [x for x in w.db.oget_contains(loc) if w.db.ohas_flag(x,EXIT_FLAG)]

def _get_dbref(w,a):

	# get "built in references
	if a == 'here':
		return w.db.oget_location(w.player)
	if a == 'me':
		return w.player 
	if a[0]=='#':
		return int(a[1:])

	# is this the name of an object the player is carrying?
	for l in w.db.oget_contains(w.player):
		if a == w.db.oget_attribute(l,NAME_ATTR):
			return l

	# is this the name of an object in the same room?
	for l in w.db.oget_contains(w.db.oget_location(w.player)):
		if a == w.db.oget_attribute(l,NAME_ATTR):
			return l 

	return w.db.nothing


def _split_command_string_on(w,args,sp):
	a = args.split(sp,1)
	return [a[0].strip(),a[1].strip()] if len(a) == 2 else [args.strip(),None]

def cmd_name(w,args):

	a = _split_command_string_on(w,args,'=')
	dbref = _get_dbref(w,a[0])

	if (dbref != w.db.nothing):
		w.db.oset_attribute(dbref,NAME_ATTR,a[1])
		print ('Named.')
	else : 
		print('Invalid format for @name command.' if a[1] == None else 
			'I don\'t see anything named ' + a[0] + ' here.')

def cmd_quit(w,args):
	w.quit()

def cmd_pose(w,args):
	print (w.db.oget_attribute(w.player,NAME_ATTR) + ' ' + args)

def cmd_semipose(w,args):
	print (w.db.oget_attribute(w.player,NAME_ATTR) + args)

def cmd_say(w,args):
	print (w.db.oget_attribute(w.player,NAME_ATTR) + ' says, "'+args+'"')

def cmd_create(w,args):
	# no quota or cost right now.
	if (args.strip() == ''):
		print ("Create what?")
	else:
		o = w.db.ocreate()
		w.db.oset_attribute(o,NAME_ATTR,args)
		w.db.omove(o,w.player)

def cmd_describe(w,args):
	a = _split_command_string_on(w,args,'=')
	dbref = _get_dbref(w,a[0])

	if (dbref != w.db.nothing):
		if (a[1] != None):
			w.db.oset_attribute(dbref,DESC_ATTR,a[1])
			print ('Described.')
		else :
			w.db.oclear_attribute(dbref,DESC_ATTR)
	else : 
		print('I don\'t see anything named ' + a[0] + ' here.')
			


def cmd_look(w,args):


	loc = w.db.oget_location(w.player)
	dbref = loc if args == '' else _get_dbref(w,args)
	if dbref == w.db.nothing:
		print ('you don\'t see anything named ' + args +' here.')
		return

	print (w.db.oget_attribute(dbref,NAME_ATTR))
	if (w.db.ohas_attribute(dbref,DESC_ATTR)):
		print (w.db.oget_attribute(dbref,DESC_ATTR))
	else :
		print (NO_DESC_MESSAGE)

	# room...
	if (dbref == loc) :
		contains = _get_room_inventory(w,dbref)
		exits = _get_room_exits(w,dbref)
		contains.remove(w.player)

		if (len(exits)>0):
			print("Exits:")
			for e in exits:
				print (w.db.oget_attribute(e,NAME_ATTR).split(';')[0])

		if (len(contains)>0):
			print ("You see:")
			for l in contains: 
				print (w.db.oget_attribute(l,NAME_ATTR))
	else:
		if (not w.db.ohas_flag(dbref,OPAQUE_FLAG)):
			contains = w.db.oget_contains(dbref)
			print (contains)			

			if (len(contains)>0):
				print ("Carrying: ")
				for l in contains: 
					print (w.db.oget_attribute(l,NAME_ATTR))


  #@dig <room name> [= <exit name>;<exit alias>*,<exit name>;<exit alias>*]
  #@dig/teleport


def _unlink_exit(w,exit):
	# should remove reference in linked room.. Currently unimplemented
	pass

def _link_exit(w,exit,todbref):
	if w.db.ohas_flag(exit,EXIT_FLAG) and w.db.ohas_flag(todbref,ROOM_FLAG):
		_unlink_exit(w,exit)
		w.db.oset_attribute(exit,DROPTO_ATTR,todbref)
 
def cmd_dig(w,args):
	a = _split_command_string_on(w,args,'=')
	
	o = w.db.ocreate()
	w.db.oset_attribute(o,NAME_ATTR,a[0])
	w.db.oset_flag(o,ROOM_FLAG)

	if (a[1] != None):
		a = _split_command_string_on(w,a[1],',')
		e1 = w.db.ocreate()
		w.db.oset_attribute(e1,NAME_ATTR,a[0])
		w.db.oset_flag(e1,EXIT_FLAG)
		w.db.omove(e1,w.db.oget_location(w.player))
		_link_exit(w,e1,o)
		if (a[1] != None):
			e2 = w.db.ocreate()
			w.db.oset_attribute(e2,NAME_ATTR,a[1])
			w.db.oset_flag(e2,EXIT_FLAG)
			w.db.omove(e2,o)
			_link_exit(w,e2,w.db.oget_location(w.player))
		

def _command_move_player(w,loc):
	w.db.omove(w.player,loc)

def cmd_dump(w,args):
	w.save("in.db")



def cmd_teleport(w,args):
	a = _split_command_string_on(w,args,'=')
	loc = _get_dbref(w,a[0]) if a[1] == None else _get_dbref(w,a[1])
	dbref = w.player if a[1] == None else _get_dbref(w,a[0])
	print ("teleporting " + str(dbref) + " to " + str(loc))

	if w.db.ohas_flag(loc,ROOM_FLAG) and not w.db.ohas_flag(dbref,ROOM_FLAG) and not w.db.ohas_flag(dbref,EXIT_FLAG):
		w.db.omove(dbref,loc)
		cmd_look(w,'')

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


def _match_exit_alias(w,e,str) :
	for n in w.db.oget_attribute(e,NAME_ATTR).split(';'):
		if n==str:
			return True
	return False



def do_commands(w) :

	args = input('> ')
	matched = False

	for e in _get_room_exits(w,w.db.oget_location(w.player)):
		if (_match_exit_alias(w,e,args)):
			_command_move_player(w,w.db.oget_attribute(e,DROPTO_ATTR))
			matched = True

	# test 1 character / nospace commands
	if (not matched) and (args[0] in _nospacecommands):
		_nospacecommands[args[0]](w,args[1:])
		matched = True

	if not matched:
		# test regular commands
		args = args.split(' ',1)
		if args[0] in _commands : 
			if len(args) == 1:
				args.append('')
			_commands[args[0]](w,args[1])
			matched = True

	if not matched: 
		print('huh?')





