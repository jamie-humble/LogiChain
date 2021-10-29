
class SmartContractDisplay {
  constructor(numb, identifier, sender, relative_type, amount, recipient, status) {
    this.numb = numb;
    this.identifier = identifier;
    this.sender = sender;
    this.relative_type = relative_type;
    this.amount = amount;
    this.recipient = recipient;
    this.status = status;
    console.log(numb, identifier, sender, relative_type, amount, recipient, status)

    this.build("smartcontract_append");
    // this.build(this.relative_type);
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
    number.innerHTML = this.numb;
    identifier.innerHTML = this.identifier;
    identifier.style = "display:none;"
    identifier.class = "identifier";
    uname.innerHTML = this.sender;
    relative_type.innerHTML = this.relative_type;
    recipient.innerHTML = this.recipient;
    amount.innerHTML = this.amount;
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
    // if (relative_order_type == "incoming" && this.status == "confirmed"){
    //   var rooter = document.getElementById("product");
    // }
    // else{
    //   var rooter = document.getElementById(relative_order_type);
    // }
    // var rooter = document.getElementById("smartcontract_append");
    $(".order_append").append(tr);
  }

}

console.log(loaded_data);
// constructor(numb, identifier, sender, relative_type, amount, recipient, status) {

//   constructor(numb, identifier, sender, relative_type, amount, recipient, status) {

var contractDisplays = [];
var i = 0;
loaded_data["orders"].forEach( x => {
  if (x["order"]["order_sender"]==loaded_data["session_node"]){
    var relative_type = "Outgoing";
  }
  else{
    var relative_type = "Incoming";
  }
  contractDisplays[i] = new SmartContractDisplay(
    i,
    x["id"],
    x["order"]["order_sender"],
    relative_type,
    x["order"]["amount"],
    x["order"]["order_recipient"],
    // x["order"]["status"]
    "pending"
  )
  i++;
});

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
    // const div2 = document.createElement("div");
    // div2.className = "col-2";
    // const img = document.createElement("img");
    // img.className = "img-fluid";
    // // item image
    // $(img).attr('src','')
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
    if (this.recipient=="receive"){
      var app = ".receive";
    }
    else if (this.recipient=="send"){
      var app = ".send";
    }
    $(app).append(div0)
  }
}

function load_products(recipient){
  nodes = ["supplier", "manufacturer", "vendor", "retailer"];
  if (recipient == "receive"){
    var pov = loaded_data["session_node"];
  }
  else if(recipient == "send"){
    var findInd = (element) => element == loaded_data["session_node"];
    var pov = nodes[1+nodes.findIndex(findInd)];
  }
  // loaded_data["products"].forEach( x => {
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
  subtotal();

  // Order information
  $(".order-info").hide();

  $(".info-hide").hide();
  $(".info-incoming").hide();

  $(".close").click(function(){
    $(".order-info").hide();
  });

  //Order creation
  $(".order-customize").hide();
  $(".payment-method").hide();
  $(".send").hide();

  $(".rec-select-another").click(function() {
    $(".submit-order").attr("aria-details","send");
    $(".order-creation").trigger("reset");
    $(".receive").hide();
    $(".send").show();
    $(".payment-method-select").attr("disabled",true);
    $(".submit-order").html("Submit Order Request");
    $(".submit-order").attr("disabled",false);
    subtotal();

  });
  $(".rec-select-me").click(function() {
    // $(".cart-summ").empty();
    $(".submit-order").attr("aria-details","receive");
    $(".order-creation").trigger("reset");
    // load_products("receive");
    $(".receive").show();
    $(".send").hide();
    $(".payment-method-select").attr("disabled",false);
    $(".submit-order").html("Submit Order");
    $(".submit-order").attr("disabled",true);
    subtotal();

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
  });
  

  $(".submit-order").click(function(){
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

  //  order info show()()()
  //     $(".order-infp").css('visibility', 'visible');


  $(function() {
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
    
    function percentageToDegrees(percentage) {
      return percentage / 100 * 360
    }
  
  });

  

  
  $( ".order-creation" ).submit(function( event ) {
    event.preventDefault();
    var product_data = [{"node":loaded_data["session_node"],"chose":$(".submit-order").attr("aria-details")}];
    $(this).serializeArray().forEach(x=>{
      if (x["value"]!=""){
        product_data.push(x);
      }
    });
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
        // console.log(err);
        new Alert("warning","Order Submission Error",err);
      }
    });
  });

  $(".choice").click(function(){
    var jsonobject = {"decision":$(this).attr("title"), "identifier":$(this).parent().parent().siblings("p").html()}
    $.ajax({
      type: "POST",
      url: "/manageescrow",
      contentType: "application/json",
      data: JSON.stringify(jsonobject),
      dataType: "json",
      success: function(response) {
        location.reload()
        alert(response.msg);
      },
      error: function(err) {
        console.log(err);
        alert(err.responseText);
      }
    });
    if (jsonobject["decision"] == "Accept"){
      alert("Please wait a moment while the XRP ledger processes your transaction.")

    }

  });

  $("#order_request").click( function(){
    $.ajax({
      type: "POST",
      url: "/createescrow",
      contentType: "application/json",
      data: JSON.stringify("request"),
      dataType: "json",
      success: function(response) {
        location.reload()
        alert(response.msg);
      },
      error: function(err) {
        console.log(err);
        alert(err.responseText);
      }
    });

  });

  $("#order_send").click(function(){
    $.ajax({
      type: "POST",
      url: "/createescrow",
      contentType: "application/json",
      data: JSON.stringify("send"),
      dataType: "json",
      success: function(response) {
        location.reload()
        alert(response.msg);
      },
      error: function(err) {
        alert(err.responseText);
      }
    });
  });


});



