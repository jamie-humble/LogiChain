# This module is used to facilitate the creation of a user, including the XRPL wallet to go with it.

import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
import hashlib
from json_handling import json_append,get_nodes
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

class Node:
  def __init__(self,type):
      self.type = type
      wallet = self.ripple_wallet()
      self.classic_address = wallet['classic_address']
      self.private_key = wallet['private_key']
      self.public_key = wallet['public_key']
      self.seed = wallet['seed']
      self.sequence = wallet['sequence']



  # Use the XRPL test network to generate an account, which is then appended to be apart of the User object
  # This user can be seen and tracked from the actual testnet at https://test.xrptoolkit.com/
  def ripple_wallet(self):
    try:
      wallet = generate_faucet_wallet(client, debug=True)
      return wallet.__dict__
      #("SUCCESS: Wallet successfully created")
    except:
      print("ERROR: Wallet could not be created")
      return ("ERROR: Wallet could not be created")

# This function detects if ANY nodes are missing from the data base and replaces the correct ones 
def construct_node_wallets():
  # Test if all of the appropriate nodes have been made accounts
  try:
    nodes_present = [x["type"] for x in list(get_nodes().values())]
    nodes_missing = [x for x in NODE_TYPES if x not in nodes_present]
    if nodes_missing == []:
      return
  except AttributeError:
    # no nodes present
    nodes_missing = NODE_TYPES
  _ = [json_append("node",Node(x).__dict__) for x in nodes_missing]
  return


  