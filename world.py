from db import *
from mush_commands import *
from player import *
import pickle
from shutil import copyfile
import os


_world_version = 1
_world_name = "PyMud"
_world = None


class World(): 

	def __init__(self):


		self.done = False
		self.name = _world_name
		self.version = _world_version

	def save(self,file) : 
		if (os.path.isfile(file)):
			copyfile(file,file+'.bak')

		f = open(file,"wb")
		pickle.dump(self.name,f)
		pickle.dump(self.version,f)
		save_db(f)
		save_player_manager(f)

	def load(self,file) : 
		f = open(file,"rb")
		self.name = pickle.load(f)
		self.version 	= pickle.load(f)
		print ("Loading database for " + self.name + " " + str(self.version)+".")
		load_db(f)
		load_player_manager(f)

	def running(self) : 
		return not self.done 

	def quit(self) :
		self.done = True


def init_world():
	global _world
	_world = World()

def create_world():
	#probably the wrong place for this code. 
	db = get_db()
	mr = db.ocreate()
	db.oset_attribute(mr,"name","Master Room")
	db.oset_attribute(mr,"desc","The master room.")
	db.oset_flag(mr,"ROOM")

def get_world():
	return _world 

	