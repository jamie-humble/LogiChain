from fire_handling import *
import random

# Here we define the products which we want nodes to be able to send between eachother 
PRODUCTS = [
  {"name": "Milk", "price":17, "seller":"supplier"},
  {"name": "Protein Powder", "price":20, "seller":"supplier"},
  {"name": "Folic Acid", "price":7, "seller":"supplier"},
  {"name": "Calcium", "price":4, "seller":"supplier"},
  {"name": "Iron Powder", "price":16, "seller":"supplier"},
  {"name": "Salt", "price":11, "seller":"supplier"},
  {"name": "First infant formula", "price":23, "seller":"vendor"},
  {"name": "Goats' milk formula", "price":34, "seller":"vendor"},
  {"name": "Hungrier baby formula", "price":46, "seller":"vendor"},
  {"name": "Comfort formula", "price":33, "seller":"vendor"},
  {"name": "Lactose-free formula", "price":38, "seller":"vendor"},
  {"name": "Soya formula", "price":32, "seller":"vendor"},
  {"name": "White Sugar", "price":6, "seller":"DEMO_supplier"},
  {"name": "Plain Flour", "price":6, "seller":"DEMO_supplier"},
  {"name": "Bulk Brownie Package", "price":100, "seller":"DEMO_manufacturer"},
  {"name": "Brownie Package", "price":50, "seller":"DEMO_vendor"}
]
# And instead of manually writing the manufactures products out, we use list comprehension to mark them up in price and send them in bulk (x10) 
markup = 5
{PRODUCTS.append({"name": "Bulk package "+x["name"], "price":(x["price"]+markup)*10, "seller":"manufacturer"}) for x in PRODUCTS if x["seller"]=="vendor"}

# This function is run as the server starts to detect if any products are missing from firebase, and to re-append them to the database if so.
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

# This is how a product is defined
class Product:
  def __init__(self, name:str, price:int, seller:str):
    self.name = name
    self.price = price
    self.seller = seller
    fire_append(PRODUCT_REF,self.__dict__)    

# This object is how we define the events which lead up to an order, essentially tracing an order back to its origin
class Tracking_Data:
  def __init__(self, order_id):
    self.order_id = order_id
    order = get_order(self.order_id)
    sending_node = order["order_sender"]
    receiving_node = order["order_recipient"]
    if order["status"] == "pending":
      self.tracking_data = self.pending(sending_node,receiving_node)
      fire_append(EVENT_REF,self.__dict__)
    elif order["status"] == "confirmed":
      try:
        update_event(self.order_id,self.confirmed(sending_node, receiving_node))
      except:
        # Since there is an edgecase where an order is generated as confirmed,
        # instead of updating data, we will need to append it to firebase 
        self.tracking_data = self.confirmed(sending_node, receiving_node)
        fire_append(EVENT_REF,self.__dict__)
    elif order["status"] == "cancelled":
      self.update_cancelled(sending_node,receiving_node)

  # This is the function which generates raw event data for a single order process
  # The commented code was written in order to flesh out the event data, giving progress updates from the delivery driver,
  # but this turns out to make event data hard to digest and so is deprecated.
  def image(self, sending_node, receiving_node):
    # https://www.usnews.com/news/best-states/rankings/infrastructure
    # possible_destinations = [
    #   "Nevada","Oregon","Washington","North Dakota","Utah",
    #   "Nebraska","Kansas","Wyoming","Minnesota","Idaho",
    #   "Georgia","Vermont","Montana","South Dakota","Colorado"
    # ]
    tracking_data = [
      "Order is to be sent by "+sending_node,
      "Awaiting approval from the "+receiving_node,
      "Approval received from the "+receiving_node,
      "The "+sending_node+" has begun prepearing the order",
      "The products have had their integrity verified",
      "The "+sending_node+" has fulfilled the order and is awaiting a delivery driver",
      "Order has been received by the delivery driver"
    ] 
    # [tracking_data.append("The delivery driver has checked into "+possible_destinations[random.randrange(0,3)]) for x in range(random.randrange(2, 10))]
    tracking_data.append("The order has successfully delivered to the "+receiving_node)
    return tracking_data

  # The pre_image function is essentially what traces an order back to its roots using the image function,
  # it loops through all nodes before the sending node and gives event data leading up to the sending node.
  def pre_image(self, sending_node, receiving_node):
    tracking_data = []
    for x in NODE_TYPES:
      if x == sending_node:
        break
      tracking_data += self.image(x, get_next_node(x))
    return tracking_data

  # Since a pending transaction has not yet been approved, we cut off the events at "awaiting approval"
  def pending(self, sending_node, receiving_node):
      tracking_data = [
        "Order sent by "+sending_node,
        "Awaiting approval from "+receiving_node
      ] 
      return self.pre_image(sending_node, receiving_node)+tracking_data

  # A confirmed transaction uses a pre_image and a curret image to show the order has arrived.
  def confirmed(self, sending_node, receiving_node):
      tracking_data = self.image(sending_node, receiving_node)
      return self.pre_image(sending_node, receiving_node)+tracking_data

# And of course a cancelled order should not be persued further than awaiting approval
  def update_cancelled(self, sending_node, receiving_node):
      tracking_data = [
        "Order sent by "+sending_node,
        "Awaiting approval from the "+receiving_node,
        "This order has been cancelled"
      ]
      tracking_data = self.pre_image(sending_node, receiving_node)+tracking_data
      update_event(self.order_id,tracking_data)
