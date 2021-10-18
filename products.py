from json_handling import *

PRODUCTS = [
  {"name": "Milk", "price":5},
  {"name": "Protein Powder", "price":20},
  {"name": "Folic Acid", "price":5},
  {"name": "Calcium", "price":5},
  {"name": "Iron Powder", "price":5},
  {"name": "Salt", "price":5},
  {"name": "Baby Formula", "price":5}
]

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
  def __init__(self, name:str, price:int):
    self.name = name
    self.price = price

    json_append("product",self.__dict__)    

