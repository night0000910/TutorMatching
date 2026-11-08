$(document).ready(function() {
    var addClassButton = document.getElementById("add-class-btn");
    var notAddClassButton = document.getElementById("not-add-class-btn");
    console.log(notAddClassButton);

    addClassButton.addEventListener("click", addTeachersClass);
    notAddClassButton.addEventListener("click", displayManageSchedule);
})

function addTeachersClass(){
    var userId = Number(document.getElementById("user-id").getAttribute("value"));
    var dummy_student_id = 1
    var year = document.getElementById("year").getAttribute("value");
    var month = document.getElementById("month").getAttribute("value");
    var day = document.getElementById("day").getAttribute("value");
    var hour = document.getElementById("hour").getAttribute("value");

    var teachers_class = {year : year, month : month, day : day, hour : hour};
    var json = JSON.stringify(teachers_class);
    console.log(json);

    var csrfToken = getCsrfToken()

    var request = new XMLHttpRequest()
    request.open("POST", "/api/v1/users/authenticated_teacher/classes/");
    request.setRequestHeader("Content-type", "application/json");
    request.setRequestHeader("X-CSRFToken", csrfToken);
    request.onload = displayManageSchedule;
    request.send(json);
}

function displayManageSchedule(){

    window.location.href = "/tutoring/manage_schedule/";

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
