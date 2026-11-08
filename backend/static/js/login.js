$(document).ready(function() {
    var loginButton = document.getElementById("login-btn");
    loginButton.addEventListener("click", login);
})

function login(){
    var userName = document.getElementById("user-name").value;
    var password = document.getElementById("password").value;

    if (userName && password){
        var usersInformation = {username : userName, password : password};
        var json = JSON.stringify(usersInformation);
        console.log(json);

        var csrfToken = getCsrfToken();

        var request = new XMLHttpRequest();
        request.open("POST", "/api/v1/login/");
        request.setRequestHeader("Content-type", "application/json");
        request.setRequestHeader("X-CSRFToken", csrfToken);
        request.onload = displayUsersPage;
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

function displayUsersPage(){
    var response = JSON.parse(this.response);
    console.log(response);
    console.log(this.status);
    var login = response.detail

    if (login == "ログインに成功しました"){
        window.location.href = "/tutoring/reserve/";

    } else{
        displayError()
    }
}

function displayError(){
    var loginFailed = document.getElementById("login-failed");

    if (loginFailed == null){
        var h6 = document.createElement("h6");
        h6.innerHTML = "ログインに失敗しました";
        h6.setAttribute("id", "login-failed");

        var div = document.getElementById("login-div");
        var loginTitle = document.getElementById("login-title");
        div.appendChild(h6);
    }
}
