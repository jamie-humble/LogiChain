import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred_obj = credentials.Certificate('logichain-113d3-7cee492b7ebe.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://logichain-113d3-default-rtdb.firebaseio.com/"
	})

REF = db.reference('/')
USER_REF = REF.child("users")
NODE_REF = REF.child("nodes")
EVENT_REF = REF.child("events")

