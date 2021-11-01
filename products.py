from fire_handling import *
import random

PRODUCTS = [
  {"name": "Milk", "price":17, "seller":"supplier"},
  {"name": "Protein Powder", "price":20, "seller":"supplier"},
  {"name": "Folic Acid", "price":7, "seller":"supplier"},
  {"name": "Calcium", "price":4, "seller":"supplier"},
  {"name": "Iron Powder", "price":16, "seller":"supplier"},
  {"name": "Salt", "price":11, "seller":"supplier"},
  {"name": "First infant formula", "price":23, "seller":"manufacturer"},
  {"name": "Goats' milk formula", "price":34, "seller":"manufacturer"},
  {"name": "Hungrier baby formula", "price":46, "seller":"manufacturer"},
  {"name": "Comfort formula", "price":33, "seller":"manufacturer"},
  {"name": "Lactose-free formula", "price":38, "seller":"manufacturer"},
  {"name": "Soya formula", "price":32, "seller":"manufacturer"}
]

markup = 5
{PRODUCTS.append({"name": "Bulk package "+x["name"], "price":(x["price"]+markup)*10, "seller":"vendor"}) for x in PRODUCTS if x["seller"]=="manufacturer"}

def product_update():
  try:
    products_present = [x["name"] for x in list(get_all_products().values())]
    products_missing = [x for x in PRODUCTS if x['name'] not in products_present]
    if products_missing == []:
      return
  except AttributeError:
    # no nodes present
    products_missing = PRODUCTS
  _ = [Product(**x) for x in products_missing]

class Product:
  def __init__(self, name:str, price:int, seller:str):
    self.name = name
    self.price = price
    self.seller = seller

    fire_append(PRODUCT_REF,self.__dict__)    

class Tracking_Data:
  def __init__(self, order_id):
    self.order_id = order_id
    order = get_order(self.order_id)
    sending_node = order["order_sender"]
    receiving_node = order["order_recipient"]
    if order["status"] == "pending":
      self.tracking_data = self.generate(sending_node,receiving_node)
      fire_append(EVENT_REF,self.__dict__)
    elif order["status"] == "confirmed":
      try:
        update_event(self.order_id,self.confirmed_tracking_data(sending_node, receiving_node))
      except:
        # Since there is an edgecase where a sontract is generated as confirmed,
        # instead of updating data, we will need to just generate it 
        self.tracking_data = self.confirmed_tracking_data(sending_node, receiving_node)
        fire_append(EVENT_REF,self.__dict__)
    elif order["status"] == "cancelled":
      self.update_cancelled(sending_node,receiving_node)


  def generate(self, sending_node, receiving_node):
      tracking_data = [
        "Order sent by "+sending_node,
        "Awaiting approval from "+receiving_node
      ] 
      return tracking_data

  def confirmed_tracking_data(self, sending_node, receiving_node):
    tracking_data = [
      "Order is to be sent by "+sending_node,
      "Awaiting approval from the "+receiving_node,
      "Approval received from the "+receiving_node,
      "The "+sending_node+" has begun prepearing the order",
      "The "+sending_node+" has fulfilled the order and is awaiting a delivery driver",
      "Order has been received by the delivery driver"
    ] 
    # https://www.usnews.com/news/best-states/rankings/infrastructure
    possible_destinations = [
      "Nevada","Oregon","Washington","North Dakota","Utah",
      "Nebraska","Kansas","Wyoming","Minnesota","Idaho",
      "Georgia","Vermont","Montana","South Dakota","Colorado"
    ]
    [tracking_data.append("The delivery driver has checked into "+possible_destinations[random.randrange(0,14)]) for x in range(random.randrange(2, 10))]
    tracking_data.append("The order has successfully delivered to the "+receiving_node)
    return tracking_data

  def update_cancelled(self, sending_node, receiving_node):
      tracking_data = [
        "Order sent by "+sending_node,
        "Awaiting approval from the "+receiving_node,
        "Approval received from the "+receiving_node,
        "This order has been cancelled"
      ]
      update_event(self.order_id,tracking_data)
