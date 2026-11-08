$(document).ready(function() {
    var addClassButton = document.getElementById("add-class-btn");
    var notAddClassButton = document.getElementById("not-add-class-btn");

    addClassButton.addEventListener("click", getClassId);
    notAddClassButton.addEventListener("click", displayChooseReservedClassDatetime);
})

function getClassId(){
    var teacherId = document.getElementById("teacher-id").getAttribute("value");
    var year = document.getElementById("year").getAttribute("value");
    var month = document.getElementById("month").getAttribute("value");
    var day = document.getElementById("day").getAttribute("value");
    var hour = document.getElementById("hour").getAttribute("value");

    var request = new XMLHttpRequest();
    request.open("GET", "/api/v1/classes/?teacher_id=" + teacherId + "&year=" + year + "&month=" + month + "&day=" + day + "&hour=" + hour);
    request.onload = addReservedClass;
    request.send();
}

function addReservedClass(){
    var response = JSON.parse(this.response);
    console.log(response);

    var classId = response.id;
    var csrfToken = getCsrfToken();
    var request = new XMLHttpRequest();
    request.open("PATCH", "/api/v1/classes/" + classId + "/");
    request.setRequestHeader("X-CSRFToken", csrfToken);
    request.onload = displayChooseReservedClassDatetime;
    request.send();

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

function displayChooseReservedClassDatetime(){
    var teacherId = document.getElementById("teacher-id").getAttribute("value");
    window.location.href = "/tutoring/choose_reserved_class_datetime/" + teacherId + "/";

}