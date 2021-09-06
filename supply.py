import json
import datetime
import xrpl
from xrpl.clients import WebsocketClient
from xrpl.transaction import safe_sign_and_autofill_transaction
import hashlib
import os
import math
import time
from xrpl.utils import xrp_to_drops
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission
from itertools import count


# This class will be used to manage session data of nodes which are currently active 
# on the webapp and will be participating in the supply chain.
class SupplyChain:
  def __init__(self):
    self.node_types = ["None", "delivery", "supplier", "manufacturer", "vendor", "retailer"]
    # self.node_stat = {"delivery":[], "supplier":[], "manufacturer":[], "vendor":[], "retailer":[]}
    self.node_stat = {x:[] for x in self.node_types}
    self.update_node_status()
    self.update_events()

  def update_events(self):
    try:
      file = open("events.json", "r")
      json_object = json.load(file)
      file.close()
    except:
      with open('events.json', "w") as file:
        json.dump([],file)
        return ("SUCCESS: empty JSON modified")

  def update_node_status(self):
    with open('users.json') as a:
      json_array = json.load(a)
    # Simple dictionary to tell us which node each user is currently assigned to
    self.user_node_dict = {x["username"]: x["node"] for x in json_array}

    for k,v in self.node_stat.items():
      for k1, v1 in self.user_node_dict.items():
        if k1 in v:
          v.remove(k1)

    for k,v in self.node_stat.items():
      for k1, v1 in self.user_node_dict.items():
        if v1 == k:
          v.append(k1)
          
  # This method has questionable efficiency, instead of only changing self.user_node_dict() and then
  # referencing the variable in another script, this method allows for us to access node data through json
  # which makes things very reliable but ive written it now. i would love some feedback as to whether i should
  # just remove this method and use local variables.
  # This being said, using JSON like this allows for people to stay a cirtain node type after rebooting the server. 
  def set_node_stat(self, username, node):
    valid = False
    for x in self.node_types:
      if node == x:
        valid = True
    if not valid: return "ERROR: Invalid node type"

    #JSON editing, first we initaiate a python object of the JSON
    file = open("users.json", "r")
    json_object = json.load(file)
    file.close()

    # then we make changes to the python object
    for x in json_object:
      if x["username"] == username:
        x["node"] = node

    # and finally replace the old json with our updates
    file = open("users.json", "w")
    json.dump(json_object, file)
    file.close()

    #update our object
    self.update_node_status()
    change = Event(username, {"bool":False},"node_change")


  def next_in_supplychain(self, _input):
    i=0
    for x in self.node_types:
      if _input == x:
        return self.node_types[i+1]
      i+=1
    return "ERROR: next node not found"

  def prev_in_supplychain(self, _input):
    i=0
    for x in self.node_types:
      if _input == x:
        return self.node_types[i-1]
      i+=1
    return "ERROR: prev node not found"

  def get_user(self, username):
    with open('users.json') as a:
      json_array = json.load(a)
    for x in json_array:
      if x["username"] == username:
        return x

  def get_users_by_node(self, node):
    with open('users.json') as a:
      json_array = json.load(a)
    arr = []
    for x in json_array:
      if x["node"] == node:
        arr.append(x)
    return arr

  def get_contract_values(self, username):
    if isinstance(username,str):
      sender = supply_chain.get_user(username)
    else:
      sender = username

    try:
      rec_wall = self.get_users_by_node(self.prev_in_supplychain(sender["node"]))[0]["wallet"]
    except:
      return "ERROR: Please make sure there is a user in "+self.prev_in_supplychain(sender["node"])
    data = {"sender_wallet": sender["wallet"],
            "recipient_wallet": rec_wall,
            # "signers": self.contract_signer_logic(sender["node"]),
            "signers": {"senders":sender["node"], "recipients":self.prev_in_supplychain(sender["node"])},
            "memo": self.contract_memo_logic(str(sender["node"])),
            "conditionals": self.generate_condition()
            }
    return data


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

  def find_contract_by_hash(self,hash):
    with open('events.json') as a:
      json_array = json.load(a)
    for x in json_array:
      if x["escrow"]["bool"] and x["escrow"]["hash"] == hash:
        return x
    return "could not be found"

  def update_contract_by_hash(self,signer,hash,mod):
    with open('events.json') as a:
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
    with open('events.json', "w") as file:
      json.dump(json_array,file)
    # return "could not be found"

  def sign(self, signer, hash):
    _contract = self.find_contract_by_hash(hash)
    # try:
    self.update_contract_by_hash(signer,hash,{"type":"append_signature"})
    _ = Event(signer, {"bool":False},"contract_signed")
    _contract = self.find_contract_by_hash(hash)
    if self.check_signature_fulfillment(_contract):
      self.update_contract_by_hash(signer,hash,{"type":"update_status","val":"confirmed"})
      return "Signature added to complete contract!"
    return "Signature added to incomplete escrow, you shouldnt really be reading this, but if you are, make sure you're not in the node role you sent the escrow to!"
    # except:
    #   return "ERROR: signature could not be added"

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
        # print(trans_signed)

        # submit transaction
        trans_response = send_reliable_submission(trans_signed, client)
        # print("\n"+str(trans_response.__dict__))

        # self.escrow["contract"] = trans_signed.to_dict()
        # self.escrow["contract_responce"] = trans_response.to_dict()
        # self.escrow["sequence"] = trans.result["tx_json"]["Sequence"]
        

        return True
    return False



# This class is used to record events and manage smart contracts
class Event:
  def __init__(self, username, escrow, event_type):
    self.username = username
    # self.nodetype = nodetype
    self.time = str(datetime.datetime.now().strftime("%x"))
    self.event_type = event_type
    self.escrow = escrow
    self.ERROR = [False, ""]

    self.node_type = supply_chain.user_node_dict[self.username]

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
          self.json_append()
    else:
      self.json_append()



  def json_append(self):
      # read json file
    with open('events.json', "r") as file:
      try:
        data = json.load(file)
      except:
        data = False
    # if the json file is empty, create an array with a dict in it
    with open('events.json', "w") as file:
      if not data: 
        json.dump([self.__dict__],file)
        return ("SUCCESS: Event appended to empty JSON")
      else:
        # if the json file is populated, add the new event 
        data.append(self.__dict__)
        # print(data)
        json.dump(data, file)
        return ("SUCCESS: Event appended to JSON")

  def create_escrow(self):
    # our smart contract function, EscrowCreate cannot intake signatures that would be needed to fullfil
    # the contract. so to work around this and also save time, we are going to fullfill the contract using 
    # a cryptographic fulfillment condition, which is given to the contract, when our PYTHON server has
    # received all needed 'signatures from the webapp'.
    # TLDR: we are not using the official blockchain signature functionality, but instead confirming
    #       signatures with python.

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

class wallet_json_to_object:
  def __init__(self, json):
    self.seed = json["seed"]
    self.public_key = json["public_key"]
    self.private_key = json["private_key"]
    self.classic_address = json["classic_address"]
    self.sequence = json["sequence"]


supply_chain = SupplyChain()