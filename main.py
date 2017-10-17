

from db import *
from mush_commands import *
from world import *
from clients import *

import os.path

def init_game(): 

	init_player_manager()
	init_db()

	init_world()
	init_commands()
	init_clients()



	if (os.path.isfile("in.db")):
		get_world().load("in.db")
	else: 
		create_world()


if __name__ == '__main__':


    logging.basicConfig(level=logging.DEBUG)

    init_game()
    world = get_world()

    while world.running():
    	update_clients()

    get_world().save("in.db")

    logging.info("Server shutdown.")



