from math import floor

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
RPC_URI = "wss://s.altnet.rippletest.net:51233"
NODE_TYPES = ["supplier", "manufacturer", "vendor", "retailer","DEMO_supplier", "DEMO_supplier", "DEMO_supplier", "DEMO_supplier"]
SHIPPING_COST = 45
XRP_CONVERSION = 0.1
XRP_TO_DROPS = lambda x : floor(x*1000000)