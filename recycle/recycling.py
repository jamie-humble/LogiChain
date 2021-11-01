  # this also runs at the start of the server to populate node_stat and create a similar var named user_node_dict, which is populated with k, v pairs in the form of username, node.
  # this seems arbitrary but it is usefull in later methods where more specific data surrounding users and their node types is required.
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
  # which makes things very reliable. i would love some feedback as to whether i should
  # just remove this method and use local variables in future.
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

    receiving_node[:1].upper()+receiving_node[1:]