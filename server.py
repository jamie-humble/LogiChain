# The purpose of this document is to run a flask server and interact with the webapp using the other two modules.

import flask
from flask import jsonify, request, session, redirect, url_for
import users
from supply import supply_chain, Event
import json
import os
import hashlib
from xrpl.clients import WebsocketClient
from xrpl.account import get_balance
from constants import *
from fire_handling import *
from products import PRODUCTS

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config.update( 
    SECRET_KEY=b'\xe8\x87\xb7\xa3\x8c\xd6;AJOEH\x90\xf2\x11\x99'
    # SECRET_KEY = os.urandom(16)
)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/signin")
def signin():
    return flask.render_template("signin.html")

@app.route("/signup")
def signup():
    return flask.render_template("signup.html")

@app.route("/postsignup", methods=['POST'])
def post_signup():
    data = request.get_json()

    if get_user(data["username"]) != False:
        return "ERROR: Username already exists"

    try:
        _ = session["users_created"]
    except:
        session["users_created"] = 0

    if session["users_created"] >= 20:
        return "You've created too many users"

    # I would have liked to make these try catches nested, but it would not stop spitting type errors at me,
    # so this pass to a non-nested try does the trick, its just a little ugly.
    # pass
    try:
        users.User(
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
        return flask.render_template("index.html")


@app.route("/dashboard/supply")
def supply():
    with open('EVENT_FILE') as a:
        json_array = json.load(a)
    supply_chain.update_node_status()
    _data = [supply_chain.__dict__, json_array]

    try: 
        # check if user is logged in
        _ = session["username"]
        return flask.render_template("supply.html", _data = _data)
    except:
        return flask.render_template("index.html")
    

@app.route("/postnodefill", methods=['POST'])
def node_filled():
    try:
        _ = session["username"]
    except: return "ERROR, user could not be found, please log back in"
    try:
        node = request.get_json()
        supply_chain.set_node_stat(session["username"],node)
        return {"msg":"SUCCESS: Node changed to "+node, "redirect": True, "redirect_url":"/dashboard/supply"}
    except:
        return "ERROR: node could not be changed"


@app.route("/LogiChain/contract")
def manage():
    # try catch will pop if session[username] is undefined -- user not logged in
    try:
        _ = session["username"]
    except:
        return flask.render_template("index.html")
    session_node = get_user(session["username"])["node"]
    _data = {"products":get_all_products(), "session_node": session_node, "orders":fetch_nodes_orders(session_node)}
    return flask.render_template("LogiDesk/manage.html", _data = json.dumps(_data))

@app.route("/order/submission", methods=['POST'])
def submit_order():
    data = request.get_json()
    participant_data = data[0]
    if participant_data["chose"] == "receive":
        order_to = participant_data["node"]
        order_from = get_prev_node(participant_data["node"])
    elif participant_data["chose"] == "send":
        order_from = participant_data["node"]
        order_to = get_next_node(participant_data["node"])
    total_price = SHIPPING_COST
    i=1
    for x in data[1:]:
        data[i]["price"] = [y["price"] for y in PRODUCTS if x["name"]==y["name"]][0]
        total_price += sum([y["price"]*int(x["value"]) for y in PRODUCTS if x["name"]==y["name"]])
        i+=1
    if participant_data["chose"] == "receive":
        fire_append(ORDER_REF,{"status":"confirmed" ,"order_sender":order_from, "order_recipient":order_to, "amount":total_price, "products":data[1:]})
        order_payment(get_node(order_to)["classic_address"],get_node(order_from),total_price)
        return {"status":"200","msg":"Your order has been created and is already signed!"}
    else:
        fire_append(ORDER_REF,{"status":"pending" ,"order_sender":order_from, "order_recipient":order_to, "amount":total_price, "products":data[1:]})
        return {"status":"200","msg":"Your order has been created and must be signed!"}

@app.route("/order/accept", methods=['POST'])
def accept_order():
    order_id = request.get_json()["id"]
    update_order_status(order_id,"accept")
    order = get_order(order_id)
    order_recipient = get_node(order["order_recipient"])
    order_sender = get_node(order["order_sender"])
    # Now we execute our order transaction
    order_payment(order_recipient["classic_address"],order_sender,order["amount"])
    return {"nature":"success","msg_title":"Order Signed","msg":"Your order has been signed and submitted to the XRP ledger!"}
    
@app.route("/order/decline", methods=['POST'])
def decline_order():
    data = request.get_json()
    update_order_status(data["id"],"decline")
    return {"nature":"warning","msg_title":"Order Declined", "msg":"You have declined and order, it is now inactive and your funds will be released"}

    

# gets account data of signed in user
@app.route("/dashboard/account")
def account():
    try:
        _ = session["username"]
    except:
        return flask.render_template("index.html")
    _data = supply_chain.get_user(_)
    with WebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
        _data["balance"] = get_balance(_data["wallet"]["classic_address"], client)
    return flask.render_template("account.html", _data = json.dumps(_data))

@app.route("/logout", methods=['POST'])
def logout():
    session["username"] = None
    print("Logout")
    return  flask.jsonify({"msg":"You have been logged out, come back soon!", "redirect": True, "redirect_url":"/"})

port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port)