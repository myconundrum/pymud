

import pickle

_nothing 		= -1
_db_version		= 2

_db = None





class object_database():

	class _object(): 

		def __init__(self):
			self.attributes = {} 		# attribute dictionary for the object
			self.contains = []   		# other objects contained in this object
			self.loc = _nothing  		# object location
			self.dbref = _nothing   	# object ID 
			self.flags = []				# object flags


	def __init__(self):

		self.objects = {}
		self.dbrefs = []				# deleted dbrefs to use
		self.nextdbref = 0				# next "new" dbref to use
		self.void = self.ocreate()
		self.nothing = _nothing 		# nothing reference. Invalid dbref
		self.version = _db_version      # version format for db.

		
	def _get_object_dbref(self):
		if (len(self.dbrefs)) : 
			i = self.dbrefs[0]
			del self.dbrefs[0]
		else : 
			i = self.nextdbref
			self.nextdbref += 1
		return i

	# creates a new object in the database. Returns object id. 
	def ocreate(self):
		o = self._object()
		o.dbref  = self._get_object_dbref()
		o.loc = _nothing
		self.objects[o.dbref] = o
		return o.dbref 

	def odelete(self,dbref) : 

		if (not self.oexists(dbref)): 
			return 

		# move inventory to void
		for i in self.objects[dbref].contains:
			omove(self,i,self.void)

		# remove from parent object.
		if (self.oexists(self.objects[dbref].loc)):
			self.objects[self.objects[dbref].loc].contains.remove(dbref)

		# add id to open dbrefs
		self.dbrefs.append(dbref) 
		# change reference to None
		self.objects.pop(dbref)


	def oexists(self,dbref):
		return dbref in self.objects
	def oget_location(self,dbref):
		return self.objects[dbref].loc if self.oexists(dbref) else _nothing
	def oget_contains(self,dbref): 
		return list(self.objects[dbref].contains) if self.oexists(dbref) else []
	def oget_attribute(self,dbref,name) : 
		return self.objects[dbref].attributes.get(name,"") if self.oexists(dbref) else ""
	def oset_attribute(self,dbref,name,value) : 
		if (self.oexists(dbref)) :
			self.objects[dbref].attributes[name]=value
	def oclear_attribute(self,dbref,name) :
		if (self.oexists(dbref)) :
			self.objects[dbref].attributes.pop(name, None)
	def ohas_attribute(self,dbref,name) :
		if (self.oexists(dbref)) :
			return name in self.objects[dbref].attributes

	def oget_all_attributes(self,dbref):
		if (self.oexists(dbref)):
			return self.objects[dbref].attributes
	def ohas_flag(self,dbref,flag) : 
		return True if self.oexists(dbref) and flag in self.objects[dbref].flags else False
	def oget_flags(self,dbref): 
		return list(self.objects[dbref].flags) if self.oexists(dbref) else []
	def oset_flag(self,dbref,flag) : 
		if (self.oexists(dbref) and flag not in self.objects[dbref].flags) :
			self.objects[dbref].flags.append(flag)
	def oclear_flag(self,dbref,flag) :
		if (self.oexists(dbref)):
			self.objects[dbref].flags.remove(flag)

	def omove(self,dbref,loc):

		if (not self.oexists(dbref)):
			print("Error: object " + str(dbref) + " does not exist.")
			return False

		o = self.objects[dbref]

		# check if destination object exists and can carry objects
		if (self.oexists(loc)):
			new = self.objects[loc]
		else: 
			print("Error: object " + str(dbref) + "can't move to " + str(loc) + "object doesn't exist")
			return False

		# remove object from existing location
		# add object to new location
		# update object location

		if (self.oexists(o.loc)):
			old = self.objects[o.loc]
			old.contains.remove(o.dbref)

		new.contains.append(o.dbref)
		o.loc = new.dbref 
		return True 



def init_db():
	global _db
	_db = object_database()

def load_db(f):
	global _db
	_db = pickle.load(f)

def save_db(f):
	pickle.dump(_db,f)

def get_db():
	return _db 



