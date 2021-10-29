import json
from constants import *
from firebase import *
import firebase_admin
import hashlib
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission, safe_sign_and_autofill_transaction
from xrpl.clients import WebsocketClient

# We are using this module to handle all of our json operations to eliminate repetition.

# The logichain prototype uses JSON files to store the supply chain's data,
# here we are using json to store the user object   

def json_append(type, data_in: dict):
  # if type == "user":
  #   ref_obj = USER_REF
  # elif type == "node":
  #   ref_obj = NODE_REF
  # elif type == "event":
  #   ref_obj = EVENT_REF
  # elif type == "product":
  #   ref_obj = PRODUCT_REF
  # elif type == "transaction":
  #   ref_obj = TRANSACTION_REF

  try:
    type.push(data_in)
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
  
def get_all_nodes():
  return NODE_REF.get()

def get_all_orders():
  return ORDER_REF.get()

def fetch_nodes_orders(node):
  # recipient = [{"id":k, "order":v} for k,v in get_all_orders().items() if v["order_recipient"]==node]
  # sender = [{"id":k, "order":v} for k,v in get_all_orders().items() if v["order_sender"]==node]
  # return {"order_recipient":recipient,"order_sender":sender}
  return [{"id":k, "order":v} for k,v in get_all_orders().items() if v["order_recipient"]==node or v["order_sender"]==node]

def get_node(type):
  for k,v in get_all_nodes().items():
    if v["type"] == type:
      return v
  return False

def get_user(username):
  for k,v in get_all_users().items():
    if v["username"] == username:
      return v
  return False

def get_next_node(node):
  i=1
  for x in NODE_TYPES:
    if x == node:
      return NODE_TYPES[i]
    i+=1
  return "ERROR: No nodes found"

def get_prev_node(node):
  i=-1
  for x in NODE_TYPES:
    if x == node:
      return NODE_TYPES[i]
    i+=1
  return "ERROR: No nodes found"


def login(username, password):
  for k,v in get_all_users().items():
    if (
      v["username"] == username and 
      v["password"] == hashlib.sha256(password.encode()).hexdigest()
    ):
      return True
  return False

# This class is used to construct a wallet object to be used in the XRPL
class wallet_json_to_object:
  def __init__(self, json):
    self.seed = json["seed"]
    self.public_key = json["public_key"]
    self.private_key = json["private_key"]
    self.classic_address = json["classic_address"]
    self.sequence = json["sequence"]

def xrpl_transaction(recipient_classic,sender_wallet_dict,amount):
  with WebsocketClient(RPC_URI) as client:
    trans = Payment(
      account= sender_wallet_dict["classic_address"],
      amount= str(amount),
      destination=recipient_classic
    )
    trans_signed = safe_sign_and_autofill_transaction(trans,wallet_json_to_object(sender_wallet_dict),client)
    # submit transaction
    trans_response = send_reliable_submission(trans_signed, client)
    if not trans_response.is_successful():
      print("ERROR: new node transaction failed!")
      return False
    # add fiat here to recipient
    return True