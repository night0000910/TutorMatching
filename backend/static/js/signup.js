$(document).ready(function() {
    $('select').formSelect();

    var signupButton = document.getElementById("signup-btn");
    signupButton.addEventListener("click", createDummyStudent);
})

function createDummyStudent(){
    var csrfToken = getCsrfToken();

    var request = new XMLHttpRequest();
    request.open("POST", "/api/v1/users/dummy_students/");
    request.setRequestHeader("Content-type", "application/json");
    request.setRequestHeader("X-CSRFToken", csrfToken);
    request.onload = signup;
    request.send();
}

function signup(){
    var userName = document.getElementById("user-name").value;
    var password = document.getElementById("password").value;
    var firstName = document.getElementById("first-name").value;
    var lastName = document.getElementById("last-name").value;
    var selectElement = document.getElementById("user-type");
    var selectedIndex = selectElement.selectedIndex;
    var userType = selectElement.options[selectedIndex].value;

    if (userName && password && userType){
        var usersInformation = {username : userName, password : password, first_name : firstName, last_name : lastName, user_type : userType};
        var json = JSON.stringify(usersInformation);
        console.log(json);

        var csrfToken = getCsrfToken();

        var request = new XMLHttpRequest();
        request.open("POST", "/api/v1/users/");
        request.setRequestHeader("Content-type", "application/json");
        request.setRequestHeader("X-CSRFToken", csrfToken);
        request.onload = displaySucceedInSignup;
        request.send(json);
    }
}

function getCsrfToken(){
    var cookies = document.cookie;
    var cookiesArray = cookies.split(";");

    for (var cookie of cookiesArray){
        var cookieArray = cookie.split("=");

        if (cookieArray[0] == "csrftoken"){
            var csrfToken = cookieArray[1];
        }
    }

    return csrfToken
}

function displaySucceedInSignup(){
    var response = JSON.parse(this.response);
    var signup = response.detail;
    console.log(signup)

    if (signup == "サインアップに成功しました"){
        window.location.href = "/tutoring/succeed_in_signup/"

    } else{
        displayError();
    }
}

function displayError(){
    var signupFailed = document.getElementById("signup-failed");

    if (signupFailed == null){
        var h6 = document.createElement("h6");
        h6.innerHTML = "サインアップに失敗しました";
        h6.setAttribute("id", "signup-failed");

        var div = document.getElementById("signup-div");
        var signupTitle = document.getElementById("signup-title");
        div.appendChild(h6);
    }
}