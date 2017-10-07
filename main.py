

from db import *
from mush_commands import *
from world import *






def main(): 

	world = World()
	init_commands()

	world.load("in.db")
	cmd_look(world,'')

	world.db.oset_flag(0,ROOM_FLAG)
		
	while (world.running()) :
		do_commands(world)




	world.save("in.db")

main()
