$(document).ready(function() {
    var button = document.getElementById("btn");
    button.addEventListener("click", displayLoginPage);
})

function displayLoginPage(){
    window.location.href = "/tutoring/login/";
}