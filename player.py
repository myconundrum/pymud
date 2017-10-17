
import pickle
from db import *

_pm = None

class PlayerEntry(): 

	def __init__(self):
		self.dbref = 0
		self.name = ""
		self.pwd = ""

class PlayerConnection():
    
    def __init__(self,client):
        self.client 	= client 
        self.dbref 		= 0 
        self.connecting = True   # While connecting is true, only process connecting commands, not all mush commands.

    def send(self,msg):
    	self.client.send(msg + '\n')

    def get_client(self):
    	return self.client

    def logout(self):
    	self.client.active = False

    def set_connecting(self,val):
    	self.connecting=val

    def is_connecting(self):
    	return self.connecting








class PlayerManager():

	def __init__(self):
		self.entries = []		# all player entries 
		self.connected = []		# connection records for current players
	
	def add_connection(self,client):
		p = PlayerConnection(client)
		p.set_connecting(True)
		self.connected.append(p)

	def remove_connection(self,p):
		self.connected.remove(p)

	def get_connected_players(self):
		return self.connected

	def connect_player(self, name, password):
		
		for e in self.entries:
			if name.lower() == e.name.lower() and password == e.pwd:
				return e.dbref

		return -1 

	def create_player(self, name, password):

		for e in self.entries:
			if name.lower() == e.name.lower():
				return -1

		p = PlayerEntry()
		db = get_db()
		p.dbref = db.ocreate()
		p.name  = name
		p.pwd   = password 
		self.entries.append(p)

		return p.dbref 





def init_player_manager():
	global _pm
	_pm = PlayerManager()
	
def get_player_manager():
	return _pm 

def load_player_manager(f):
	global _pm
	_pm.entries = pickle.load(f)

def save_player_manager(f):
	pickle.dump(_pm.entries,f)




