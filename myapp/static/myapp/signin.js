console.log("welcome");
function getCookie(c_name) {
    if(document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if(c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if(c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$("#loginSubmit").click(function(e){
    var user = $("#txtUser").val() || null;
    var pass = $("#txtPassword").val() || null;
    e.preventDefault();
    $.ajax({
        type:"POST",
        url:"/headerSignIn/",
        headers : {
            "X-CSRFToken": getCookie("csrftoken")
        },
        data: {
            'data': [user,pass],
        },
        success: function(data){
            $("#dialogBoxLogin").empty();
            if(data == "Does not match"){
                $("#dialogBoxLogin").append("<p style='color:white;'>Username and password do not match our records</p>");
                return 0;
            }
            else {
                console.log("done");
                window.location.replace("/");
            }
        }
    });
});