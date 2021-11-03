// This module is used to create dynamic alerts for the webpage.
class Alert{
  constructor(nature,heading,content){
    this.nature = nature;
    this.heading = heading;
    this.content = content;
    this.build();
  }
  build(){
    const alert_div = document.createElement("div");

    // Make dismissible
    $(alert_div).addClass("alert alert-dismissible fade show shadow-sm alert-info position-absolute top-0 start-50 translate-middle-x");
    $(alert_div).attr("role", "alert");
    $(alert_div).css("margin", "20px");
    // Ensure that the alert cant be covered by any other content 
    $(alert_div).css("z-index", "99999");

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

    const cancel_span = document.createElement("span");
    $(cancel_span).attr("aria-hidden", "true");
    cancel_span.innerHTML = "&times;";
    cancel.appendChild(cancel_span);

    [head, divider, text, cancel].forEach(x => {
      alert_div.appendChild(x);
    });
    // Append to a predetermined container
    $(".alert-container").prepend(alert_div);
    
    $(".alert").click(function(){
      $(".alert").alert('close');
    });
  }
}

window.Alert = Alert;