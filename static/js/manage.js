// This is the JS file responsible for the handling of orders 

// First we have the class which is populated by LogiChain Orders.
// this class works to simply display an order
class OrderDisplay {
  constructor(numb, identifier, sender, relative_type, amount, recipient, status, products) {
    this.numb = numb;
    this.identifier = identifier;
    this.sender = sender.slice(0,1).toUpperCase()+sender.slice(1);
    this.recipient = recipient.slice(0,1).toUpperCase()+recipient.slice(1);
    this.relative_type = relative_type;
    this.amount = amount;
    this.status = status;
    this.products = products;
    this.build("smartcontract_append");
  }

  build(relative_order_type){
    // creation
    const tr = document.createElement("tr");
    const number = document.createElement("td");
    const uname = document.createElement("td");
    const relative_type = document.createElement("td");
    const amount = document.createElement("td")
    const recipient = document.createElement("td");
    const activity = document.createElement("td");
      const activity_span = document.createElement("span");
    const identifier = document.createElement("p");

    // Buttons to manage contract
    const td = document.createElement("td");
      const a0 = document.createElement("a");
        const i0 = document.createElement("i");
      const a1 = document.createElement("a");
        const i1 = document.createElement("i");
 

    // should change dependant on status of contract
    // text-danger: red, text-warning:yellow, text-success:green
    tr.className = "order_entry"
    number.innerHTML = this.numb;
    identifier.innerHTML = this.identifier;
    identifier.style = "display:none;"
    identifier.class = "identifier";
    uname.innerHTML = this.sender;
    relative_type.innerHTML = this.relative_type;
    recipient.innerHTML = this.recipient;
    amount.innerHTML = "$"+this.amount;
    activity_span.style = "padding:0 0 10px 10px;"

    switch(this.status) {
      case "cancelled":
        activity_span.className = "status text-danger";
        activity_span.innerHTML = "&bull;";
        activity.innerHTML = "Inactive";
        break;
      case "pending":
        activity_span.className = "status text-warning";
        activity_span.innerHTML = "&bull;";
        activity.innerHTML = "Pending";
        if (relative_order_type == "incoming"){
          a0.className = "settings";
          // a0.data-toggle = "tooltip";
          i0.className = "material-icons choice";
          i0.innerHTML = "&#xe86c;";
          i0.title = "Accept";
          a1.className = "Delete";
          // a1.data-toggle = "tooltip";
          i1.className = "material-icons choice";
          i1.innerHTML = "&#xE5C9;";
          i1.title = "Delete";
      
          // DOM Distribution
          a1.appendChild(i1);
          a0.appendChild(i0);
          td.appendChild(a1);
          td.appendChild(a0);
        }

        break;
      case "confirmed":
        activity_span.className = "status text-success";
        activity_span.innerHTML = "&bull;";
        activity.innerHTML = "Fulfilled";
        break;

    }
    activity.appendChild(activity_span);

    [number,uname, recipient,relative_type,amount,activity,td,identifier].forEach(x => {
      tr.appendChild(x);
    });
    $(".order_append").append(tr);
  }
}
// This code works to generate every relevant order 
var ORDER_MASTER_ARRAY = [];
var i = 0;
loaded_data["orders"].forEach( x => {
  if (x["order"]["order_sender"]==loaded_data["session_node"]){
    var relative_type = "Outgoing";
  }
  else{
    var relative_type = "Incoming";
  }
  ORDER_MASTER_ARRAY[i] = new OrderDisplay(
    i,
    x["id"],
    x["order"]["order_sender"],
    relative_type,
    x["order"]["amount"],
    x["order"]["order_recipient"],
    x["order"]["status"],
    x["order"]["products"]
  )
  i++;
});
// If there are no orders to generate, fill the page with a nice "no orders" image and message
if(i==0){
  const img_no_orders = document.createElement("img");
  $(img_no_orders).attr("src","/static/img/no-orders.png");
  $(img_no_orders).css("height","100%");
  $(img_no_orders).css("width","100%");
  const h_no_orders = document.createElement("h1");
  $(h_no_orders).attr("class", "h2 text-center");
  $(h_no_orders).css("margin-bottom", "100px");
  $(h_no_orders).html("There are no orders for you right now, why not make one!")
  $(".container-xl").append(h_no_orders);
  $(".container-xl").append(img_no_orders);
}

// To give information about a specific order, show the purchased products
class Info_Product_Display {
  constructor(amount, item, price) {
    this.amount = "x "+amount;
    this.item = item;
    this.price = "$"+price;
    this.build();
  }

  build(){
    // Create the necessary elements
    const tr = document.createElement("tr");
    const amount = document.createElement("td");
    const item = document.createElement("td");
    const price = document.createElement("td");
 
    amount.innerHTML = this.amount;
    item.innerHTML = this.item;
    price.innerHTML = this.price;

    [amount,item,price].forEach(x => {
      tr.appendChild(x);
    });

    $(".info_order_summary_append").append(tr);
  }
}
// Give Context of the order in past, allowing a user to track it back to its roots
class Event_Display {
  constructor(event) {
    this.event = event;
    this.build();
  }

  build(){
    // Create the necessary elements
    const tr = document.createElement("tr");
    const event = document.createElement("td");
    $(event).html(this.event);

    tr.appendChild(event);
    $(".event_append").append(tr);
  }
}

// This class is used to construct the available products for someone to include in an order 
class ProductDisplay{
  constructor(title, price, recipient){
    this.title = title;
    this.price = price;
    this.recipient = recipient;
    this.build();
  }
  build(){
    const div0 = document.createElement("div");
    div0.className = "row border-top border-bottom";
    const div1 = document.createElement("div");
    div1.className = "row align-items-center";
    const div3 = document.createElement("div");
    div3.className = "col";
    const div4 = document.createElement("div");
    div4.className = "row";
    // item name
    div4.innerHTML = this.title;
    const div5 = document.createElement("div");
    div5.className = "col product-inputs";
    const minus = document.createElement("a");
    minus.innerHTML = "-";
    minus.className = "minus";
    const input = document.createElement("input");
    input.className = "border item-number";
    $(input).attr("type","number");
    // name = product type
    $(input).attr("name",this.title);
    const plus = document.createElement("a");
    plus.innerHTML = "+";
    plus.className = "plus";
    const div6 = document.createElement("div");
    div6.className = "col product-price";
    // price
    div6.innerHTML = "&dollar;"+this.price;

    // child appending
    // starting with top level
    // div2.appendChild(img);
    div3.appendChild(div4);
    div5.appendChild(minus);
    div5.appendChild(input);
    div5.appendChild(plus);
    // base level
    [div3,div5,div6].forEach(x =>{
      div1.appendChild(x);
    });
    div0.appendChild(div1);
    // Here, we append each product to a specific div so that depending on who the order is
    // sent by, the right products are shown. 
    if (this.recipient=="receive"){
      var app = ".receive";
    }
    else if (this.recipient=="send"){
      var app = ".send";
    }
    $(app).append(div0)
  }
}

const nodes = ["supplier", "manufacturer", "vendor", "retailer", "DEMO_supplier", "DEMO_manufacturer", "DEMO_vendor", "DEMO_retailer"];


// Fucntion to generate the right products for each order.
function load_products(recipient){
  if (recipient == "send"){
    var pov = loaded_data["session_node"];
  }
  else if(recipient == "receive"){
    var findInd = (element) => element == loaded_data["session_node"];
    var pov = nodes[nodes.findIndex(findInd)-1];
  }
  for (const [key, value] of Object.entries(loaded_data["products"])){
    if (value["seller"] == pov){
      var _ = new ProductDisplay(value["name"],value["price"],recipient);
    }
  }
}
load_products("receive");
load_products("send");

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Function to find the total price of an order when its being created.
function subtotal(){
  var sub_total=0;
  $(".item-number").each(function(){
    var price = $(this).parent().next(".col").html();
    var price = Number(price.substring(1));
    sub_total += $(this).val()*price;
  })
  window.order_total = sub_total;
  $(".subtotal").html("&dollar;"+sub_total);
  $(".total").html("&dollar;"+(sub_total+45));
}


$(document).ready(function(){
  const Alert = window.Alert;


  // Order information
  $(".order-info").hide();
  $(".info-hide").hide();
  $(".info-incoming").hide();
  $(".close").click(function(){
    $(".order-info").hide();
  });

  //Order creation
  subtotal();
  $(".order-customize").hide();
  $(".payment-method").hide();
  $(".send").hide();

  // The two following functions are called when, in order creation, a user presses the send or receive button, respectively. 
  function send_select(){
    // Give hidden information to an element
    $(".submit-order").attr("aria-details","send");
    // Reset the form each time a button is pressed
    $(".order-creation").trigger("reset");
    // Show the appropriate products
    $(".receive").hide();
    $(".send").show();
    // Change buttons
    $(".payment-method-select").attr("disabled",true);
    $(".submit-order").html("Submit Order Request");
    $(".submit-order").attr("disabled",false);
    subtotal();
    // Give a bit of context to the order
    $(".recip-info").html("You ("+loaded_data["session_node"]+") will be sending products to "+nodes[nodes.indexOf(loaded_data["session_node"])+1])
  }

  function receive_select(){
    $(".submit-order").attr("aria-details","receive");
    $(".order-creation").trigger("reset");
    $(".receive").show();
    $(".send").hide();
    $(".payment-method-select").attr("disabled",false);
    $(".submit-order").html("Submit Order");
    $(".submit-order").attr("disabled",true);
    subtotal();
    $(".recip-info").html("You ("+loaded_data["session_node"]+") will be receiving products from "+nodes[nodes.indexOf(loaded_data["session_node"])-1])

  }

  // Order creation button logic
  $(".rec-select-send").click(function() {
    send_select();
  });
  $(".rec-select-receive").click(function() {
    receive_select();
  });

  $(".payment-method-select").click(function(){
    $(".payment-method").show();
    $(".order-customize-cont").hide();
  });

  $(".visa").click(function(){
    $(".continue-payment").attr("disabled",false);
  });

  $(".continue-payment").click(function(){
    $(".payment-method").hide();
    $(".order-customize-cont").show();
    $(".submit-order").attr("disabled",false);
  });

  $(".cancel-order").click(function(){
    $(".order-customize").hide();
  });

  $(".create-order").click(function(){
    $(".order-customize").show();
    $(".order-customize").css('visibility', 'visible');
    $(".recip-info").html("You ("+loaded_data["session_node"]+") will be receiving products from "+nodes[nodes.indexOf(loaded_data["session_node"])-1])

    if(loaded_data["session_node"]=="supplier"||loaded_data["session_node"]=="DEMO_supplier"){
      $(".rec-select-receive").attr("disabled",true);
      $(".rec-select-send").attr("checked",true);
      $(".rec-select-receive").attr("checked",false);

      send_select();
    }
    else if(loaded_data["session_node"]=="retailer"||loaded_data["session_node"]=="DEMO_retailer"){
      $(".rec-select-send").attr("disabled",true);
      receive_select();
    }
  });
  // Button logic end
  
  // Function to update the radial progress bar 
  function percentageToDegrees(percentage) {
    return percentage / 100 * 360
  }
  function progress() {
    $(".progress").each(function() {
  
      var value = $(this).attr('data-value');
      var left = $(this).find('.progress-left .progress-bar');
      var right = $(this).find('.progress-right .progress-bar');
  
      if (value > 0) {
        if (value <= 50) {
          right.css('transform', 'rotate(' + percentageToDegrees(value) + 'deg)')
        } else {
          right.css('transform', 'rotate(180deg)')
          left.css('transform', 'rotate(' + percentageToDegrees(value - 50) + 'deg)')
        }
      }
    })
  } 

  // When an order is clicked on, show its information
  $(".order_entry").click(function(){
    // Make the order information container visible
    $(".info_order_summary_append").empty();
    $(".order-info").show();
    $(".info-hide").show();
    $(".info-incoming").show();
    $(".order-info").css('visibility', 'visible');

    // Get information
    var id = $(this).find("p").html();
    for (let index = 0; index < ORDER_MASTER_ARRAY.length; index++) {
      const x = ORDER_MASTER_ARRAY[index];
      if (x.identifier == id){
        var order_object = x;
      }
    }
    // Check if the ID was found
    try{
      var _ = order_object;
    }
    catch{
      return new Alert("error","Order not found","We could not find the order you selected, please reload the page and try again.")
    }
    // Display information
    if (order_object["recipient"].slice(0,4) != "DEMO"){
      order_object["sender"] = order_object["sender"].toLowerCase();
      order_object["recipient"] = order_object["recipient"].toLowerCase();
  
    }

    if(order_object["status"] == "pending"){
      if(loaded_data["session_node"] == order_object["recipient"]){
        // Allow the recipient to accept/decline the order
        $(".accept-order").show();
        $(".decline-order").show();

        $(".accept-order").attr("disabled",false);
        $(".decline-order").attr("disabled",false);  
      }
      else{
        console.log(loaded_data["session_node"], order_object["recipient"],order_object["recipient"].slice(0,4))
        // Allow the sender to cancel the order
        $(".accept-order").attr("disabled",true);
        $(".accept-order").hide();
        $(".decline-order").attr("disabled",false);
        $(".decline-order").html("Cancel Order");
      }
    }

    else if(order_object["status"] == "confirmed" || order_object["status"] == "cancelled"){
      $(".accept-order").hide();
      $(".decline-order").hide();
    }
    $(".accept-order").attr("id",id);
    $(".decline-order").attr("id",id);

    if(order_object["status"] == "pending"){
      $(".progress").attr("data-value","25");
      $(".progress-percent").html("25");
      $(".progress-preparation").html("50%");
      $(".progress-delivery").html("0%");
      $(".QR-code-select").hide();
      progress();
    }
    else if(order_object["status"] == "confirmed"){
      $(".progress").attr("data-value","100");
      $(".progress-percent").html("100");
      $(".progress-preparation").html("100%");
      $(".progress-delivery").html("100%");
      $(".QR-code-select").show();
      $(".QR-code-select").attr("id",id);
      progress();
    }
    else if(order_object["status"] == "cancelled"){
      $(".progress").attr("data-value","0");
      $(".progress-percent").html("0");
      $(".progress-preparation").html("100%");
      $(".progress-delivery").html("0%");
      $(".QR-code-select").hide();
      progress();
    }
    // Display the orders products
    order_object.products.forEach(x=>{
      var _ = new Info_Product_Display(x["value"],x["name"],x["price"]) 
    });
    $(".info-total").html(order_object["amount"]);

    // Display the order's events
    for (const [key, value] of Object.entries(loaded_data["events"])){
      if (value["order_id"] == id){
        value["tracking_data"].forEach(x => {
          new Event_Display(x);
        });
      }
    }
    $(".event_append").scrollTop($(".event_append")[0].scrollHeight);
  });
  // END order display
  // Submission functions
  $(".submit-order").click(function(){
    $(".submit-order").attr("disabled",true);
    try{
      if(window.order_total==0){
        return new Alert("warning", "Select some items", "Before proceeding with your order, please select some products.");
      }
    }
    catch(err){
      return new Alert("warning", "Select some items", "Before proceeding with your order, please select some products.");
    }
    $(".order-creation").submit();
  });

  $( ".order-creation" ).submit(function( event ) {
    event.preventDefault();
    var submit_aria = $(".submit-order").attr("aria-details")
    var product_data = [{"node":loaded_data["session_node"],"chose":submit_aria}];
    for (let index = 0; index < $(this).serializeArray().length; index++) {
      const x = $(this).serializeArray()[index];
      if (x["value"] % 1 != 0){
        // Ive tried my best to stay professional during this project, but since this only occurs if someone really wants to
        // break my website, ill allow a little bit of cheek 
        return new Alert("warning","Float Detected", "You cant buy half of a product you silly billy!");
      }
      else if (x["value"]!=""){
        product_data.push(x);
      }
      
    }

    if (submit_aria=="receive"){
      new Alert("success","Your Order's Payment is Processing", "This may take a minute, please wait while the XRP ledger processes your order.")

    }
    $.ajax({
      type: "POST",
      url: "/order/submission",
      contentType: "application/json",
      data: JSON.stringify(product_data),
      dataType: "json",
      success: function(response) {
        new Alert("success","Order Submitted",response.msg);
        location.reload();
      },
      error: function(err) {
        console.log(err);
        new Alert("warning","Order Submission Error",err.responseText);
      }
    });
  });

  // Allows for people to add or take products with the click of a button
  $(".minus").click(function() {
    var input = $(this).next('input');
    var numb = Number($(input).val())-5;
    $(input).val(numb);
    if (numb == "NaN" || numb < 0){
      $(input).val(0);
    }
    subtotal();
  });
  $(".plus").click(function() {
    var input = $(this).prev('input');
    var numb = Number($(input).val())+5;
    $(input).val(numb);
    if ((input).val() == "NaN" || numb < 0){
      $(input).val(0);
    }
    subtotal();
  });

  $(".item-number").keyup(function(){
    subtotal();
  });  

  $(".accept-order").click(function(){
    var id = $(this).attr("id");
    new Alert("success","Your Order's Payment is Processing", "This may take a minute, please wait while the XRP ledger processes your order.")
    $.ajax({
      type: "POST",
      url: "/order/accept",
      contentType: "application/json",
      data: JSON.stringify({"id":id}),
      dataType: "json",
      success: function(response) {
        new Alert(response.nature,response.msg_title,response.msg);
        location.reload()
      },
      error: function(err) {
        console.log(err);
        new Alert("warning","Order Management Error",err.responseText);
      }
    });
  });
  $(".decline-order").click(function(){
    var id = $(this).attr("id");
    $.ajax({
      type: "POST",
      url: "/order/decline",
      contentType: "application/json",
      data: JSON.stringify({"id":id}),
      dataType: "json",
      success: function(response) {
        new Alert(response.nature,response.msg_title,response.msg);
        location.reload()
      },
      error: function(err) {
        console.log(err);
        new Alert("warning","Order Management Error",err.responseText);
      }
    });
  });
  // END Order Submission functions


  // QR API
  $(".QR-code-select").click(function(){
    var id = $(this).attr("id");
    $.ajax({
      type: "POST",
      url: "/LogiDesk/order/qr/generate",
      contentType: "application/json",
      data: JSON.stringify({"id":id}),
      dataType: "json",
      success: function(response) {
        new Alert("success",response.msg_title,response.msg);
        window.location.href = "order/qr/show";
      },
      error: function(err) {
        console.log(err);
        new Alert("warning","Order Management Error",err.responseText);
      }
    });
  });
});



