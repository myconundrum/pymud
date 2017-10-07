from db import *
from mush_commands import *
import pickle
from shutil import copyfile
import os


_world_version = 1

class World(): 

	def __init__(self):


		self.done = False
		self.db =  object_database()
		self.version = _world_version
		self.player = 1


	def save(self,file) : 
		if (os.path.isfile(file)):
			copyfile(file,file+'.bak')

		f = open(file,"wb")
		pickle.dump(self.version,f)
		pickle.dump(self.player,f)
		pickle.dump(self.db,f)


	def load(self,file) : 
		f = open(file,"rb")
		self.version 	= pickle.load(f)
		self.player 	= pickle.load(f)
		self.db 		= pickle.load(f)


	def running(self) : 
		return not self.done 

	def quit(self) :
		self.done = True

	