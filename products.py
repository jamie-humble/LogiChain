from fire_handling import *

PRODUCTS = [
  {"name": "Milk", "price":5, "seller":"supplier"},
  {"name": "Protein Powder", "price":20, "seller":"supplier"},
  {"name": "Folic Acid", "price":5, "seller":"supplier"},
  {"name": "Calcium", "price":5, "seller":"supplier"},
  {"name": "Iron Powder", "price":5, "seller":"supplier"},
  {"name": "Salt", "price":5, "seller":"supplier"},
  {"name": "First infant formula", "price":30, "seller":"manufacturer"},
  {"name": "Goats' milk formula", "price":20, "seller":"manufacturer"},
  {"name": "Hungrier baby formula", "price":45, "seller":"manufacturer"},
  {"name": "Comfort formula", "price":35, "seller":"manufacturer"},
  {"name": "Lactose-free formula", "price":30, "seller":"manufacturer"},
  {"name": "Soya formula", "price":30, "seller":"manufacturer"}
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

