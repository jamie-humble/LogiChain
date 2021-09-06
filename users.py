import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
import hashlib

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

class User:
  def __init__(self, username, password):
    self.username = username
    # Here we will use sha256 to hash passwords as securely as possible, like a real coder.
    # In order for a user to log in, we simply hash the password they provide and see if it 
    # matches this hash, as we see in line 39 of server.py.
    self.password = hashlib.sha256(password.encode()).hexdigest()
    self.node = "None"
    # a user should always have a unique username
    self.ripple_wallet()
    self.json_append()


  def json_append(self):
        # read json user file
    with open('users.json', "r") as file:
      try:
        data = json.load(file)
      except:
        data = False
    # if the json file is empty, create an array with a user dict in it
    with open('users.json', "w") as file:
      if not data: 
        json.dump([self.__dict__],file)
        return ("SUCCESS: User appended to empty JSON")
      else:
        # if the json file is populated, add the new user 
        data.append(self.__dict__)
        # print(data)
        json.dump(data, file)
        return ("SUCCESS: User appended to JSON")

  def ripple_wallet(self):
    try:
      wallet = generate_faucet_wallet(client, debug=True)
      self.wallet = wallet.__dict__
      return ("SUCCESS: Wallet successfuly created")
    except:
      return ("ERROR: Wallet could not be created")


import os
# there should be an admin node always in the None type
with open('users.json', "r") as file:
      try:
        # if .json is empty, we make an admin
        data = json.load(file)
      except:
        data = False

      if not data: 
        admin = User("admin",str(os.urandom(10)))
