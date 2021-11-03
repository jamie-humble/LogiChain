# Hello and welcome to the LogiChain Repo!

I would recommend reading in this order:
- Python
  - server.py
  - firebase.py
  - fire_handling.py
  - constants.py
  - users.py
  - products.py
- JavaScript
  - static\js\sign.js
  - static\js\manage.js
  - static\js\alerts.js

To access the deployment of LogiChain you have two options:
1. You should try access it through heroku app at https://logichain.herokuapp.com/
2. if not, run server.py in console with the below requirements and connect to the port in a browser.

## Requirements
flask
xrpl-py
firebase_admin
qrcode[pil]

# Run this to install
> pip3 install flask, xrpl-py, firebase_admin, qrcode[pil]

# Usage
LogiChain is a fairly intuitive application, so extensive direction should not be necessary, but as far as functionality goes:
- When a user lands on the application, they should sign up by pressing the "Get Started" button.
- Once in the app, you should navigate to "orders" and create one.
  - When creating an order, if "receive" is selected an order will immediately be validated and sent.
  - However if "send" is selected, the order will be pending, and must be signed by the receiving node.
- Once an order is created, you can opt to generate a QR code for it.
  - Simply scan this code with your phone and you will be able to track the order back to its origin, with the supplier.