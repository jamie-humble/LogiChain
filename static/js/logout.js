
$(document).ready(function(){
  $(".logout").click(function(){
    $.ajax({
      type: "POST",
      url: "/logout",
      contentType: "application/json",
      data: {"Logout":true},
      dataType: "json",
      success: function(response) {
        location.href = response.redirect_url
        new Alert("success","Successfully Logged Out",response.msg);
      },
      error: function(err) {
        console.log(err);
        alert(err.responseText);
      }
    });
  });
});