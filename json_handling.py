import json
from constants import *


# We are using this module to handle all of our json operations to eliminate repetition.

# The logichain prototype uses JSON files to store the supply chain's data,
# here we are using json to store the user object   
def json_append(filename: str, data_in: dict):
  # read json user file
  with open(filename, "r") as file:
    try:
      data = json.load(file)
    except:
      data = False
  # if the json file is empty, create an array with a user dict in it
  with open(filename, "w") as file:
    if not data: 
      json.dump([data_in],file)
      return ("SUCCESS: data appended to empty JSON")
    else:
      # if the json file is populated, add the new user 
      data.append(data_in)
      # print(data)
      json.dump(data, file)
      return ("SUCCESS: data appended to JSON")

def event_cleared_repair():
  try:
    file = open("EVENT_FILE", "r")
    json_object = json.load(file)
    file.close()
  except:
    with open('EVENT_FILE', "w") as file:
      json.dump([],file)
      return ("SUCCESS: empty JSON modified")

