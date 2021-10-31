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
from firebase import EVENT_REF
# from firebase import EVENT_REF
from fire_handling import fire_append
from users import construct_node_wallets
from constants import *
from products import product_update


# the supplyChain class controls almost all methods to do with users, escrows and the supply chain, this is because the Event class is never actually stored by the server.
# the fact that most webapp data is stored on the JSON files and that supply_chain is the only global variable stored across modules means that this class must be capable of handling
# methods based off JSON data.
class SupplyChain:
  def __init__(self):
    #node_types more or less controlls the basic logic of the node interaction, for example when a contract is made by the n'th node, it is simply sent to the n+1'th node 
    # Node status monitors which users are currently apart of each nodetype based off JSON data
    self.node_stat = {x:[] for x in NODE_TYPES}
    print(construct_node_wallets())
    product_update()


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
          fire_append(EVENT_REF,self.__dict__)
    else:
      fire_append(EVENT_REF,self.__dict__)



supply_chain = SupplyChain()