# This module is used to facilitate the creation of a user, including the XRPL wallet to go with it.

import hashlib
from fire_handling import *
from constants import *
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import WebsocketClient, JsonRpcClient
from xrpl.account import get_balance


# store global variables which control which network we are connecting to
client = JsonRpcClient(JSON_RPC_URL)

class User:
  def __init__(self, username, password, role, firstname, lastname, email, phone):
    self.username = username
    # Here we will use sha256 to hash passwords as securely as possible, like a real coder.
    # In order for a user to log in, we simply hash the password they provide and see if it 
    # matches this hash.
    self.password = hashlib.sha256(password.encode()).hexdigest()
    self.node = role
    self.firstname = firstname
    self.lastname = lastname
    self.email = email
    self.phone = phone
    # a user should always have a unique username
    fire_append(USER_REF, self.__dict__)

class Node:
  def __init__(self,type):
    self.type = type
    self.fiat_balance = 0
    wallet = self.ripple_wallet()
    self.classic_address = wallet['classic_address']
    self.private_key = wallet['private_key']
    self.public_key = wallet['public_key']
    self.seed = wallet['seed']
    self.sequence = wallet['sequence']

    self.transact(wallet)

  def transact(self,wallet):
    # If the node is an admin, or the admin cant be found, return
    if self.type == "LogiChain-Admin":
      return
    admin = get_node("LogiChain-Admin")
    if admin == False:
      return "No admin user"

    # We find the balance of the new account and store it so that we can transact it out into the admin account.
    with WebsocketClient(RPC_URI) as client:
      balance = get_balance(self.classic_address, client)

    # Minus 10,000,000 drops from the amount being transacted for the account to hold its base reserve
    # https://xrpl.org/reserves.html#base-reserve-and-owner-reserve
    return xrpl_transaction(admin["classic_address"], self.__dict__, balance-10000000)
    
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
  nodes_needed = ["LogiChain-Admin"]+NODE_TYPES[:]
  try:
    nodes_present = [x["type"] for x in list(get_all_nodes().values())]
    nodes_missing = [x for x in nodes_needed if x not in nodes_present]
    if nodes_missing == []:
      return
  except AttributeError:
    # no nodes present
    nodes_missing = nodes_needed
  _ = [fire_append(NODE_REF,Node(x).__dict__) for x in nodes_missing]
  return


  