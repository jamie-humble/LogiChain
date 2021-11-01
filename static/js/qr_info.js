console.log(loaded_data)
class Info_Product_Display {
  constructor(amount, item, price) {
    this.amount = "x "+amount;
    this.item = item;
    this.price = "$"+price;
    this.build();
    // this.build(this.relative_type);
  }

  build(){
    // creation
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

class Event_Display {
  constructor(event) {
    this.event = event;
    this.build();
    // this.build(this.relative_type);
  }

  build(){
    // creation
    const tr = document.createElement("tr");
    const event = document.createElement("td");
    $(event).html(this.event);

    tr.appendChild(event);
    $(".event_append").append(tr);
  }
}

for (const [key, value] of Object.entries(loaded_data["events"])){
  if (value["order_id"] == loaded_data["id"]){
    value["tracking_data"].forEach(x => {
      new Event_Display(x);
    });
  }
}

loaded_data["products"].forEach(x=>{
  var _ = new Info_Product_Display(x["value"],x["name"],x["price"]) 
});

$(".info-total").html(loaded_data["total"]);

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