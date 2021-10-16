{/* <div class="alert alert-success" role="alert">
  <h4 class="alert-heading">Well done!</h4>
  <p>Aww yeah, you successfully read this important alert message. This example text is going to run a bit longer so that you can see how spacing within an alert works with this kind of content.</p>
  <hr>
  <p class="mb-0">Whenever you need to, be sure to use margin utilities to keep things nice and tidy.</p>
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>
</div> */}

class Alert{
  constructor(nature,heading,content){
    this.nature = nature;
    this.heading = heading;
    this.content = content;
    this.build();
  }
  build(){
    const alert_div = document.createElement("div");

    // make dismissible
    $(alert_div).addClass("alert alert-dismissible fade show shadow-sm alert-info position-absolute top-0 start-50 translate-middle-x");
    $(alert_div).attr("role", "alert");
    $(alert_div).css("margin", "20px");
    $(alert_div).css("z-index", "999");

    switch (this.nature) {
      case "success":
        $(alert_div).addClass("alert-success");
        break;
      case "error":
        $(alert_div).addClass("alert-danger");
        break;
      case "warning":
        $(alert_div).addClass("alert-warning");
        break;
      default:
        $(alert_div).addClass("alert-primary");
        break;
    }
    const head = document.createElement("h4");
    $(head).addClass("alert-heading");
    head.innerHTML = this.heading;
    const divider = document.createElement("hr");
    const text = document.createElement("p");
    text.innerHTML = this.content;
    const cancel = document.createElement("button");
    $(cancel).attr("type", "button");
    $(cancel).attr("class", "close");
    $(cancel).attr("data-dismiss", "alert");
    $(cancel).attr("aria-label", "close");
    // $(cancel).css("z-index", "9999");

    const cancel_span = document.createElement("span");
    $(cancel_span).attr("aria-hidden", "true");
    cancel_span.innerHTML = "&times;";
    cancel.appendChild(cancel_span);

    [head, divider, text, cancel].forEach(x => {
      alert_div.appendChild(x);
    });
    // document.body.appendChild(alert_div);
    // $(alert_div).insertAfter("#header");
    $(".container").prepend(alert_div);
    
    $(".alert").click(function(){
      $(".alert").alert('close');
    });
  }
}



window.Alert = Alert;