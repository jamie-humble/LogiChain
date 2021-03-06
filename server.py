# The purpose of this document is to run a flask server and interact with the webapp using the other modules.

import flask
from flask import request, session
from users import *
from constants import *
from fire_handling import *
from products import PRODUCTS, Tracking_Data, product_update
import json
import os
import qrcode


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config.update( 
    # The secret key identifies which session data flask should use, if we want to reset out session, we would
    # use the urandom() function to create and save a new secret key. 
    SECRET_KEY=b'\xe8\x87\xb7\xa3\x8c\xd6;AJOEH\x90\xf2\x11\x99'
    # SECRET_KEY = os.urandom(16)
)

# These functions make sure that the necessary objects are present in firebase, the nodes and products.
construct_node_wallets()
product_update()

# I will only comment on this basic route function once,
# It simply tells the server which HTML file to show when a cirtain URL is hit. 
@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/signin")
def signin():
    return flask.render_template("signin.html")

@app.route("/signup")
def signup():
    return flask.render_template("signup.html")

# This function is a receiver for an API from the signup page which will attempt to create a new user 
# using the data received from the API.
@app.route("/postsignup", methods=['POST'])
def post_signup():
    data = request.get_json()

    if get_user(data["username"]) != False:
        return "ERROR: Username already exists"

    # First, detect any Manindras and stop them from making 4000 users again.
    try:
        _ = session["users_created"]
    except:
        session["users_created"] = 0

    if session["users_created"] >= 20:
        return "You've created too many users"
    try:
        # Create user, which will be appended to firebase in the User object  
        User(
            data["username"], 
            data["password"], 
            data["role"], 
            data["firstname"],
            data["lastname"],
            data["email"],
            data["phone"]
        )
        session["username"] = data["username"]
        session["users_created"] += 1
        # For an API reciever, its important that their is a returned value which felflects the success of the API call, we do this here
        # and throughout the rest of the script. 
        return {"msg":"Congrats! You've successfully created a LogiChain account", "redirect": True, "redirect_url":"/LogiDesk"}
    except FileNotFoundError:
        return {"msg":"ERROR: User could not be created", "redirect": False, "redirect_url":""}


@app.route("/postsignin", methods=['POST'])
def post_signin():
    data = request.get_json()
    # find user and sign in
    if login(data["username"],data["password"]):
        session["username"] = data["username"]
        return {"msg":"Congrats! you've signed into LogiChain", "redirect": True, "redirect_url":"/LogiDesk"}
    return "ERROR: Incorrect username or password"

@app.route("/LogiDesk")
def check():
    # this try expression is to catch whether or not a user is signed in
    try: 
        _ = session["username"]
        return flask.render_template("LogiDesk/index.html")
    except:
        return flask.render_template("signin.html")
    
# This function acts as a page route but it also transmits data to be processed bt javascript and used to display information on the webpage.
@app.route("/LogiDesk/order")
def manage():
    # try catch will pop if session[username] is undefined -- user not logged in
    try:
        _ = session["username"]
    except:
        return flask.render_template("signin.html")
    session_node = get_user(session["username"])["node"]
    _data = {"products":get_all_products(), "session_node": session_node, "orders":fetch_nodes_orders(session_node), "events":get_all_events()}
    return flask.render_template("LogiDesk/manage.html", _data = json.dumps(_data))

@app.route("/order/submission", methods=['POST'])
def submit_order():
    data = request.get_json()
    participant_data = data[0]
    # We use the API data to decern who the order is addressed to.
    if participant_data["chose"] == "receive":
        order_to = participant_data["node"]
        order_from = get_prev_node(participant_data["node"])
    elif participant_data["chose"] == "send":
        order_from = participant_data["node"]
        order_to = get_next_node(participant_data["node"])
    # Then we begin to evaluate the total cost of the order.
    total_price = SHIPPING_COST
    i=1
    for x in data[1:]:
        data[i]["price"] = [y["price"] for y in PRODUCTS if x["name"]==y["name"]][0]
        total_price += sum([y["price"]*int(x["value"]) for y in PRODUCTS if x["name"]==y["name"]])
        i+=1
    # Then we append our order data to firebase, depending on the recipient of the order, it will either be instantly payed for, or it will need to be signed. 
    if participant_data["chose"] == "receive":
        order_id = fire_append(ORDER_REF,{"status":"confirmed" ,"order_sender":order_from, "order_recipient":order_to, "amount":total_price, "products":data[1:]})
        # This is the first instance we see of tracking_data, which is used to track the origin of an order all the way back to the supplier node.
        Tracking_Data(order_id)
        order_payment(get_node(order_from),get_node(order_to),total_price)
        return {"status":"200","msg":"Your order has been created and is already signed!"}
    else:
        order_id = fire_append(ORDER_REF,{"status":"pending" ,"order_sender":order_from, "order_recipient":order_to, "amount":total_price, "products":data[1:]})
        Tracking_Data(order_id)
        return {"status":"200","msg":"Your order has been created and must be signed!"}

# An API to accept orders
@app.route("/order/accept", methods=['POST'])
def accept_order():
    order_id = request.get_json()["id"]
    # Record the signing of the order and change the status of the order.
    update_order_status(order_id,"accept")
    Tracking_Data(order_id)
    order = get_order(order_id) 
    order_recipient = get_node(order["order_recipient"])
    order_sender = get_node(order["order_sender"])
    # Now we execute our order payment
    try:
        order_payment(order_recipient,order_sender,order["amount"])
        return {"nature":"success","msg_title":"Order Signed","msg":"Your order has been signed and submitted to the XRP ledger!"}
    except:
        return {"nature":"error","msg_title":"Order Could not be signed","msg":"Please reload the page and try again"}

        
# An API to decline orders by simply chaing their status
@app.route("/order/decline", methods=['POST'])
def decline_order():
    data = request.get_json()
    update_order_status(data["id"],"decline")
    Tracking_Data(data["id"])
    return {"nature":"warning","msg_title":"Order Declined", "msg":"You have declined and order, it is now inactive and your funds will be released"}

# Once this API is hit with an order ID, it generates a QR code to view the order information.
@app.route("/LogiDesk/order/qr/generate", methods=['POST'])
def qr_generate():
    order_id = request.get_json()["id"]
    # Store the order ID in the URL of the QR code
    img = qrcode.make('logichain.herokuapp.com/LogiDesk/order/qr/?id='+str(order_id))
    img.save("static/img/qr/order_qr.png")
    return {"msg_title":"QR code created","msg":"You will now be redirected to your QR code"}

# Once the QR code is made above, the QR code is displayed through this webpage. 
@app.route("/LogiDesk/order/qr/show")
def qr_show():
    return flask.render_template("LogiDesk/qr_code.html")    

# When a QR code is scanned, this route is hit, feeding an order info page information about the order in question.
# This page will usually be accessed through a phone as that will be the easiest to scan the QR code, but once its ready,  
@app.route("/LogiDesk/order/qr/")
def qr_info():
    order_id = request.args.get("id")
    order = get_order(order_id)
    _data = {"id":order_id, "events":get_event(order_id), "products":order["products"], "total":order["amount"]}
    return flask.render_template("LogiDesk/qr_code_info.html", _data = json.dumps(_data))   

# Display the account of a user
@app.route("/LogiDesk/account")
def account():
    try:
        _ = session["username"]
    except:
        return flask.render_template("signin.html")
    _data = get_node(get_user(session["username"])["node"])
    _data["username"] = session["username"]
    return flask.render_template("LogiDesk/account.html", _data = json.dumps(_data))

@app.route("/logout", methods=['POST'])
def logout():
    session["username"] = None
    return  flask.jsonify({"msg":"You have been logged out, come back soon!", "redirect": True, "redirect_url":"/"})



port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port)