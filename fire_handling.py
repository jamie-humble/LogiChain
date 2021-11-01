import json
from constants import *
from firebase import *
import firebase_admin
import hashlib
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_transaction,send_reliable_submission, safe_sign_and_autofill_transaction
from xrpl.clients import WebsocketClient
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_balance
from math import ceil
from xrpl.wallet import generate_faucet_wallet

# We are using this module to handle all of our json operations to eliminate repetition.

# The logichain prototype uses JSON files to store the supply chain's data,
# here we are using json to store the user object   

def fire_append(ref_type, data_in: dict):
  try:
    push = ref_type.push(data_in)
    return push.key
  except:
    return "Data could not be pushed to database"

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

def get_all_events():
  return EVENT_REF.get()

def fetch_nodes_orders(node):
  if get_all_orders() == None: return []
  return [{"id":k, "order":v} for k,v in get_all_orders().items() if v["order_recipient"]==node or v["order_sender"]==node]

def get_order(id):
  for k,v in get_all_orders().items():
    if k == id:
      return v
  return False

def get_node(node_type):
  for k,v in get_all_nodes().items():
    if v["type"] == node_type:
      return v
  return False

def get_node_object(node_type):
  for k,v in get_all_nodes().items():
    if v["type"] == node_type:
      return {"key":k,"value":v}
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

def get_event(order_id):
  for k,v in get_all_events().items():
    if v["order_id"] == order_id:
      return {"key":k,"value":v}
  return False

def login(username, password):
  for k,v in get_all_users().items():
    if (
      v["username"] == username and 
      v["password"] == hashlib.sha256(password.encode()).hexdigest()
    ):
      return True
  return False

def update_fiat_balance(node, amount):
  node_obj = get_node_object(node)
  balance = int(node_obj["value"]["fiat_balance"])+amount
  fire_object = NODE_REF.child(node_obj["key"])
  fire_object.update({
    "fiat_balance":balance
  })

def update_event(order_id,tracking_data):
  event_id = get_event(order_id)["key"]
  fire_object = EVENT_REF.child(event_id)
  fire_object.update(tracking_data)


# This class is used to construct a wallet object to be used in the XRPL
class wallet_json_to_object:
  def __init__(self, json):
    self.seed = json["seed"]
    self.public_key = json["public_key"]
    self.private_key = json["private_key"]
    self.classic_address = json["classic_address"]
    self.sequence = json["sequence"]

def xrpl_admin_fund(amount):
  """
    This function should look like this, but since the XRP network wont let you transact
    straight from its admin node, this function is creating new XRP accounts and stripping
    them of their funds to give to the LogiChain admin.

    transaction = Payment(
      account = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
      amount = str(amount),
      destination = admin_classic["classic_address"],
      sequence = get_latest_validated_ledger_sequence(client),
      fee = "10" 
    )
    transaction_send = submit_transaction(transaction,client)
    print(transaction_send)
  """
  with WebsocketClient(RPC_URI) as client:
    admin = get_node("LogiChain-Admin")
    balance = get_balance(admin["classic_address"], client)
    if balance > amount:
      return True
    
    drop_from_each = XRP_TO_DROPS(1000)
    accs_needed = ceil(amount/drop_from_each)
    for x in range(accs_needed):
      wallet = generate_faucet_wallet(client, debug=True).__dict__
      wallet["type"] = "Temporary Wallet"
      xrpl_transaction(admin["classic_address"], wallet, 990000000)
      print("Wallet #"+str(x)+" has been emptied")


def xrpl_transaction(recipient_classic,sender_wallet_dict,amount):
  with WebsocketClient(RPC_URI) as client:
    trans = Payment(
      account = sender_wallet_dict["classic_address"],
      amount = str(amount),
      destination = recipient_classic
    )
    trans_signed = safe_sign_and_autofill_transaction(trans,wallet_json_to_object(sender_wallet_dict),client)
    # submit transaction
    trans_response = send_reliable_submission(trans_signed, client)
    if not trans_response.is_successful():
      print("ERROR: new node transaction failed!")
      return False
    print("Transaction from "+sender_wallet_dict["type"]+" for "+str(amount)+" drops")
    return True

def order_payment(recipient_wallet_dict, sender_wallet_dict, fiat_amount):

  """
  This function is based on the model of LogiChain's payment system.
  The idea is that, since each node is technically a client, a node should not
  be holding XRP as an asset for longer than absolutely necessary.
  This is because, at the end of the day, XRP is an asset and its value fluctuates,
  this means that if they are holding XRP for a long time clients or nodes of LogiChain 
  are at risk of losing money through the assets value dropping.
  The way that LogiChain gets around this problem is by having an admin node, which 
  holds the XRP needed for the clients transactions.

  When a client makes a transaction, they should not initially have any XRP in their 
  wallet to fund the transaction, so LogiChain's admin node sends them enough XRP to fund the
  transaction in exchange for the client's fiat (dollars) currency.
  This way, the admin acts as a centralized exchange for the supply chain and eliminates the
  risk of clients losing their money.
  In the context of this assignment, LogiChain is operating on a test network, which means 
  the admin node can practically have an unlimited amount of XRP, but in a real buisness scenario,
  LogiChain would be buying from a propper exchange to fund the admin node, which funds the client nodes.
  """
  recipient_classic = recipient_wallet_dict["classic_address"]
  # amount is in the form of drops, so we find the number of XRP with fiat_amount*XRP_CONVERSION
  # and then turn it into drops.
  amount = XRP_TO_DROPS(fiat_amount*XRP_CONVERSION)
  # First we will fund the admin node
  xrpl_admin_fund(amount)
  # Second, we transfer funds from the admin node to the client
  admin_object = get_node("LogiChain-Admin")
  xrpl_transaction(sender_wallet_dict["classic_address"], admin_object,amount)
  # Finally, we execute the orders transaction
  xrpl_transaction(recipient_classic, sender_wallet_dict, amount)
  # Now, to protect the client from loss, we take away their XRP in exchange for fiat money
  xrpl_transaction(admin_object["classic_address"],recipient_wallet_dict,amount)
  update_fiat_balance(recipient_wallet_dict["type"],fiat_amount)



def update_order_status(id,nature):
  fire_object = ORDER_REF.child(id)
  if nature == "accept":
    fire_object.update({
      "status":"confirmed"
    })
    return True
  elif nature == "decline":
    fire_object.update({
      "status":"cancelled"
    })
    return True
  return False

