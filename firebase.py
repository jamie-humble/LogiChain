import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred_obj = credentials.Certificate('logichain-113d3-7cee492b7ebe.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://logichain-113d3-default-rtdb.firebaseio.com/"
	})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('restricted_access/secret_document')
print(ref.get())