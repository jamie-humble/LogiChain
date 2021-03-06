$(document).ready(function(){
  const Alert = window.Alert;

  // Submit form on button click
  $("#submit").click(function(){
    $(this).closest("form").submit();
  });
  
  $(".signup").submit(function( event ) {
    event.preventDefault();
    const data = new FormData(event.target);
    const value = Object.fromEntries(data.entries());
    // Dont allow empty feilds
    for (const [key, val] of Object.entries(value)) {
      if (val == ""){
        return new Alert("warning",'Empty Field(s) Detected',"Please fill out all of the forms fields.");
      }
    }

    // Check that the passwords match
    if(value["passwordConfirmation"]!=value["password"]){
      return new Alert("warning",'Passwords do not match.',"Try to carefully re-enter your password confirmation.");
    }

    // Stop people trying to break the server
    if(/^[a-zA-Z0-9-]*$/.test(value["username"] + value["password"]) == false) {
      return new Alert("warning","Illegal Characters Detected",'Your username or password contains illegal characters.');
    }

    // Send API
    $.ajax({
      type: "POST",
      url: "/postsignup",
      contentType: "application/json",
      data: JSON.stringify(value),
      dataType: "json",
      success: function(response) {
        
        new Alert("success","Signed Up",response.msg);
        if (response.redirect){
          window.location.href = response.redirect_url;
        }
      },
      error: function(err) {
        console.log(err);
        new Alert("error","ERROR",err.responseText);
      }
    });
  });

  $(".signin").submit(function( event ) {
    event.preventDefault();
    const data = new FormData(event.target);
    const value = Object.fromEntries(data.entries());

    for (const [key, val] of Object.entries(value)) {
      if (val == ""){
        return new Alert("warning",'Empty Field(s) Detected',"Please fill out all fields.");
      }
    }
    
    if(/^[a-zA-Z0-9- ]*$/.test(value["username"]+value["password"]) == false) {
      return new Alert("warning","Illegal Characters Detected",'Your username or password contains illegal characters.');
    }

    $.ajax({
      type: "POST",
      url: "/postsignin",
      contentType: "application/json",
      data: JSON.stringify(value),
      dataType: "json",
      success: function(response) {
        
        new Alert("success","Signed In",response.msg);
        if (response.redirect){
          window.location.href = response.redirect_url;
        }
      },
      error: function(err) {
        console.log(err);
        new Alert("error","Could not sign in!",err.responseText);
      }
    });
  });
});

