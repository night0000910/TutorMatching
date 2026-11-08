$(document).ready(function() {
    var csrfToken = getCsrfToken();

    var request = new XMLHttpRequest();
    request.open("POST", "/api/v1/logout/");
    request.setRequestHeader("X-CSRFToken", csrfToken);
    request.onload = displayHomePage;
    request.send();
})

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

function displayHomePage(){
    console.log(JSON.parse(this.response));
    window.location.href = "/tutoring/home_page/";
}