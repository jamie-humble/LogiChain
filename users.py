# This module is used to facilitate the creation of a user, including the XRPL wallet to go with it.

import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
import hashlib
from json_handling import json_append
from constants import *

# store global variables which control which network we are connecting to
client = JsonRpcClient(JSON_RPC_URL)

class User:
  def __init__(self, username, password, role, firstname, lastname, email, phone):
    self.username = username
    # Here we will use sha256 to hash passwords as securely as possible, like a real coder.
    # In order for a user to log in, we simply hash the password they provide and see if it 
    # matches this hash, as we see in line 39 of server.py.
    self.password = hashlib.sha256(password.encode()).hexdigest()
    self.node = role
    self.firstname = firstname
    self.lastname = lastname
    self.email = email
    self.phone = phone
    # a user should always have a unique username
    json_append("user", self.__dict__)

# import os
# # there should be an admin node always in the None type
# with open(NODE_FILE, "r") as file:
#       try:
#         # if .json is empty, we make an admin
#         data = json.load(file)
#       except:
#         data = False

#       if not data: 
#         admin = User("admin",str(os.urandom(10)))

class Node:
  def __init__(self,type):
      self.type = type
      self.wallet = self.ripple_wallet()

  # Use the XRPL test network to generate an account, which is then appended to be apart of the User object
  # This user can be seen and tracked from the actual testnet at https://test.xrptoolkit.com/
  def ripple_wallet(self):
    try:
      wallet = generate_faucet_wallet(client, debug=True)
      return wallet.__dict__
      #("SUCCESS: Wallet successfully created")
    except:
      return ("ERROR: Wallet could not be created")

def construct_node_wallets():
  node_types = ["delivery", "supplier", "manufacturer", "vendor", "retailer"]

  # read json user file
  with open(NODE_FILE, "r") as file:
    try:
      data = json.loads(file.read())
    except:
      data = False
  # if the json file is empty, create an array with a user dict in it
  if not data: 
    with open(NODE_FILE, "w") as file:
      json_in = [Node(x).__dict__ for x in node_types]
      json.dump(json_in,file)
      return ("SUCCESS: data appended to empty JSON")
  return "JSON data already present"

  