import json
from constants import *
from firebase import *
import firebase_admin
import hashlib


# We are using this module to handle all of our json operations to eliminate repetition.

# The logichain prototype uses JSON files to store the supply chain's data,
# here we are using json to store the user object   

def json_append(type:str, data_in: dict):
  if type == "user":
    ref_obj = USER_REF
  elif type == "node":
    ref_obj = NODE_REF
  elif type == "event":
    ref_obj = EVENT_REF
  elif type == "product":
    ref_obj = PRODUCT_REF

  try:
    ref_obj.push(data_in)
    return "Data pushed to database"
  except:
    return "Data could not be pushed to database"

# def json_append(filename: str, data_in: dict):
#   # read json user file
#   with open(filename, "r") as file:
#     try:
#       data = json.load(file)
#     except:
#       data = False
#   # if the json file is empty, create an array with a user dict in it
#   with open(filename, "w") as file:
#     if not data: 
#       json.dump([data_in],file)
#       return ("SUCCESS: data appended to empty JSON")
#     else:
#       # if the json file is populated, add the new user 
#       data.append(data_in)
#       # print(data)
#       json.dump(data, file)
#       return ("SUCCESS: data appended to JSON")
def get_all_users():
  get = USER_REF.get()
  if get == None:
    return {}
  return get

def get_all_products():
  return PRODUCT_REF.get()
  
def get_nodes():
  return NODE_REF.get()


def get_user(username):
  for k,v in get_all_users().items():
    if v["username"] == username:
      return v
  return False

def login(username, password):
  for k,v in get_all_users().items():
    if (
      v["username"] == username and 
      v["password"] == hashlib.sha256(password.encode()).hexdigest()
    ):
      return True
  return False

