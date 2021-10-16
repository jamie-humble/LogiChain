# The purpose of this module is to handle all internal logic of the supply chain, including node interaction, escrows, payments and
# other methods that must be given to server.py .

import json
import datetime
import xrpl
from xrpl.clients import WebsocketClient
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.utils import xrp_to_drops
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission
import hashlib
import os
import math
import time
from itertools import count
from json_handling import json_append
from users import construct_node_wallets
from constants import *


NODETYPES = ["delivery", "supplier", "manufacturer", "vendor", "retailer"]

# the supplyChain class controls almost all methods to do with users, escrows and the supply chain, this is because the Event class is never actually stored by the server.
# the fact that most webapp data is stored on the JSON files and that supply_chain is the only global variable stored across modules means that this class must be capable of handling
# methods based off JSON data.
class SupplyChain:
  def __init__(self):
    #node_types more or less controlls the basic logic of the node interaction, for example when a contract is made by the n'th node, it is simply sent to the n+1'th node 
    # Node status monitors which users are currently apart of each nodetype based off JSON data
    self.node_stat = {x:[] for x in NODETYPES}
    print(construct_node_wallets())

  # simply finds the next node in the supply chain 
  def next_in_supplychain(self, _input):
    i=0
    for x in NODETYPES:
      if _input == x:
        return NODETYPES[i+1]
      i+=1
    return "ERROR: next node not found"

  # simply finds the previous node in the supply chain 
  def prev_in_supplychain(self, _input):
    i=0
    for x in NODETYPES:
      if _input == x:
        return NODETYPES[i-1]
      i+=1
    return "ERROR: prev node not found"

  # this is used to find an entire user object based off a unique username
  def get_user(self, username):
    with open(USER_FILE) as a:
      json_array = json.load(a)
    for x in json_array:
      if x["username"] == username:
        return x

  # returns all the users of a specific node type
  def get_users_by_node(self, node):
    with open(USER_FILE) as a:
      json_array = json.load(a)
    arr = []
    for x in json_array:
      if x["node"] == node:
        arr.append(x)
    return arr

  # returns a contract value dict based off the sender of the contract
  def get_contract_values(self, username):
    # this function is called at multiple points, where not all points have enough info to pass the whole user object,
    # so we just account for those cases by getting the ser based off a username. 
    if isinstance(username,str):
      sender = supply_chain.get_user(username)
    else:
      sender = username

    try:
      recipient_wallet = self.get_users_by_node(self.prev_in_supplychain(sender["node"]))[0]["wallet"]
    except:
      return "ERROR: Please make sure there is a user in "+self.prev_in_supplychain(sender["node"])
    data = {"sender_wallet": sender["wallet"],
            "recipient_wallet": recipient_wallet,
            # "signers": self.contract_signer_logic(sender["node"]),
            "signers": {"senders":sender["node"], "recipients":self.prev_in_supplychain(sender["node"])},
            "memo": self.contract_memo_logic(str(sender["node"])),
            "conditionals": self.generate_condition()
            }
    return data

  # the next 3 methods just find specific information for get_contract_values
  def contract_signer_logic(self, sender_node_type):
    return {"senders": [x["username"] for x in self.get_users_by_node(sender_node_type)], "recipients": [x["username"] for x in self.get_users_by_node(self.prev_in_supplychain(sender_node_type))]}

  def contract_memo_logic(self, sender_node_type):
    msg = "The "+sender_node_type+" node made a contract to send "+self.prev_in_supplychain(sender_node_type)+" some products."
    return msg

  def generate_condition(self):
    random = hashlib.sha256(str(os.urandom(16)).encode()).hexdigest()
    hash = hashlib.sha256(random.encode()).hexdigest()

    return {
      "condition":hash.upper(), 
      "fulfillment":random.upper()
    }

  # returns a contract object based off of its unique hash value
  def find_contract_by_hash(self,hash):
    with open('EVENT_FILE') as a:
      json_array = json.load(a)
    for x in json_array:
      if x["escrow"]["bool"] and x["escrow"]["hash"] == hash:
        return x
    return "could not be found"

  # this method is used to update the JSON of a contract when changes have been made in python
  def update_contract_by_hash(self,signer,hash,mod):
    with open('EVENT_FILE') as a:
      json_array = json.load(a)
    i=0
    for x in json_array:
      if x["escrow"]["bool"] and x["escrow"]["hash"] == hash:
        if mod["type"] == "append_signature":
          json_array[i]["escrow"]["signatures"].append(supply_chain.get_user(signer)["node"])
          break
        if mod["type"] == "update_status":
          json_array[i]["escrow"]["status"] = mod["val"] 
          break
        elif mod["type"] == "cancel_status":
          json_array[i]["escrow"]["status"] = mod["val"] 
          break
      i+=1
    with open('EVENT_FILE', "w") as file:
      json.dump(json_array,file)
    # return "could not be found"

  # logic to sign a contract, which updates json and creates an event to display the signing event on the webapp
  def sign(self, signer, hash):
    _contract = self.find_contract_by_hash(hash)
    try:
      self.update_contract_by_hash(signer,hash,{"type":"append_signature"})
      _ = Event(signer, {"bool":False},"contract_signed")
      _contract = self.find_contract_by_hash(hash)
      if self.check_signature_fulfillment(_contract):
        self.update_contract_by_hash(signer,hash,{"type":"update_status","val":"confirmed"})
        return "Signature added to complete contract!"
      return "Signature added to incomplete escrow, you shouldn't really be reading this, but if you are, make sure you're not in the node role you sent the escrow to!"
    except:
      return "ERROR: signature could not be added"

  # logic to cancel a contract, which updates json and creates an event to display the canceled event on the webapp
  def cancel(self, signer, hash):
    _contract = self.find_contract_by_hash(hash)
    try:
      self.update_contract_by_hash(signer,hash,{"type":"cancel_signature"})
      _ = Event(signer, {"bool":False},"contract_cancelled")
      _contract = self.find_contract_by_hash(hash)
      # if self.check_signature_fulfillment(_contract):
      self.update_contract_by_hash(signer,hash,{"type":"update_status","val":"cancelled"})
      return "Contract declined!"
    except:
      return "ERROR: contract could not be declined"

  # checks whether all users have signed and if so, execute the transaction on XRPL
  def check_signature_fulfillment(self, obj):
    # Check if all signers have signed
    if obj["escrow"]["signatures"] == ([obj["escrow"]["signers"]["recipients"]]+[obj["escrow"]["signers"]["senders"]]):
      data = self.get_contract_values(obj["username"])

      # Once we know that our condition has been met, we are able to utilize the XRPL testnet to send transactions between our users.
      # Origionally, this was supposed to use escrows or smart contracts, but after 10+ hours of troubleshooting i have decided
      # to settle for transactions which are enabled by local conditions instead of crypto conditions.
      # For a prototype, i am happy to get atleast this working as it is a minimum viable product.  

      # we have a local object to be constructed from json data and used in the transaction
      if isinstance(data,str) and data[:5] == "ERROR":
        return data
      _wallet = wallet_json_to_object(data["sender_wallet"])

      # create a XRPL transaction object, this is not yet on the ledger, we must first sign and submit it
      trans = Payment(
        account=data["sender_wallet"]["classic_address"],
        amount=xrp_to_drops(50),
        destination=data["recipient_wallet"]["classic_address"]
      )

      # sign transaction
      with WebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
        trans_signed = safe_sign_and_autofill_transaction(trans,_wallet,client)

        # submit transaction
        trans_response = send_reliable_submission(trans_signed, client)
        return True
    return False



# This class is used to record events on JSON and manage smart contracts
class Event:
  def __init__(self, username, escrow, event_type):
    self.username = username
    self.time = str(datetime.datetime.now().strftime("%x"))
    self.event_type = event_type
    self.escrow = escrow
    self.ERROR = [False, ""]

    self.node_type = supply_chain.user_node_dict[self.username]

    # create event messages to show on webpage
    if event_type == "node_change":
      supply_chain.update_node_status()
      if self.node_type == "None": self.node_type = "spectator"
      self.memo = self.username+" has become a "+self.node_type+" node!"
    elif event_type == "contract_signed":
      supply_chain.update_node_status()
      if self.node_type == "None": self.node_type = "spectator"
      self.memo = self.username+" the "+self.node_type+", has signed a contract!"
    elif event_type == "contract_cancelled":
      self.meme = self.username+" the "+self.node_type+", has canceled a contract!"
    
    if self.escrow["bool"]:
      check = self.create_escrow()
      if isinstance(check,str):
        if check[:5] == "ERROR":
          self.ERROR[0] = True
          self.ERROR[1] = self.create_escrow()
          print("Event() escaped", self.ERROR)
        else:
          json_append('event',self.__dict__)
    else:
      json_append('event',self.__dict__)

  # This function is used to create a JSON reprisentation of a smart contract, since XRPL will not let us create an actuall
  # escrow, when this 'contract' is filfilled we will send an XRPL transaction.
  def create_escrow(self):
    data = supply_chain.get_contract_values(self.username)
        
    # if there is no user to receive transaction, return error msg higher up
    if isinstance(data,str):
      return data
    rippleOffset = 946684800
    cancelAfter = math.floor(time.time() - rippleOffset + (24*60*60))

    # currently the destination address is only one user (the first one of a node type), fix this upon deployment 
    value_dict = {
      "account": data["sender_wallet"]["classic_address"], 
      "amount": xrp_to_drops(self.escrow["amount"]),
      "condition": data["conditionals"]["condition"],
      "cancel_after": cancelAfter,
      "destination": data["recipient_wallet"]["classic_address"]
    }
    
    self.node = supply_chain.get_user(data["signers"]["recipients"][0])
    self.escrow["value_dict"] = value_dict
    self.escrow["hash"] = self.escrow["value_dict"]["condition"]

    self.escrow["status"] = "pending"
    self.escrow["memo"] = data["memo"]
    self.escrow["signers"] = data["signers"]
    self.escrow["signatures"] = [data["signers"]["recipients"]]

    return "Smart contract created"

# This class is used to construct a wallet object to be used in the XRPL
class wallet_json_to_object:
  def __init__(self, json):
    self.seed = json["seed"]
    self.public_key = json["public_key"]
    self.private_key = json["private_key"]
    self.classic_address = json["classic_address"]
    self.sequence = json["sequence"]


supply_chain = SupplyChain()