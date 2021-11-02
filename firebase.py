import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Here we are initiating our firebase session with our credentials as an admin
cred_obj = credentials.Certificate('logichain-113d3-7cee492b7ebe.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://logichain-113d3-default-rtdb.firebaseio.com/"
	})

# And we initiate global variables to be used for interacting with certain objects
REF = db.reference('/')
USER_REF = REF.child("users")
NODE_REF = REF.child("nodes")
EVENT_REF = REF.child("events")
PRODUCT_REF = REF.child("products")
ORDER_REF = REF.child("orders")

