$(document).ready(function() {
    var userId = document.getElementById("user-id").getAttribute("value");

    var request = new XMLHttpRequest();
    request.open("GET", "/api/v1/users/" + userId + "/");
    request.onload = displayUsersInformation;
    request.send();
})

function displayUsersInformation(){
    var response = JSON.parse(this.response);
    var user = response

    var image = user.profile_image;
    var firstName = user.first_name;
    var lastName = user.last_name;
    var selfIntroduction = user.self_introduction;

    var profileImage = document.getElementById("profile-image");
    var firstNameForm = document.getElementById("first-name");
    var lastNameForm = document.getElementById("last-name");
    var selfIntroductionForm = document.getElementById("self-introduction");

    profileImage.setAttribute("src", image);
    firstNameForm.setAttribute("value", firstName);
    lastNameForm.setAttribute("value", lastName);
    selfIntroductionForm.innerHTML = selfIntroduction;

    var updateImageButton = document.getElementById("update-image-btn");
    var updateNameButton = document.getElementById("update-name-btn");
    var updateSelfIntroductionButton = document.getElementById("update-self-introduction-btn");

    updateImageButton.addEventListener("click", updateImage);
    updateNameButton.addEventListener("click", updateName);
    updateSelfIntroductionButton.addEventListener("click", updateSelfIntroduction);

    var imageForm = document.getElementById("image-form");
    imageForm.addEventListener("change", readImageFile);

}

function readImageFile(){
    var imageForm = document.getElementById("image-form");
    var fileReader = new FileReader();
    
    for (file of imageForm.files){
        fileReader.readAsDataURL(file);

        fileReader.onload = function (){
            dataURL = fileReader.result;
        };
    }
}

function updateImage(){

    if (dataURL != null){
        var file = {"file" : dataURL};
        var json = JSON.stringify(file);

        var csrfToken = getCsrfToken();

        var request = new XMLHttpRequest();
        request.open("PATCH", "/api/v1/users/authenticated_user/profile_image/");
        request.setRequestHeader("X-CSRFToken", csrfToken);
        request.setRequestHeader("Content-type", "application/json");
        request.onload = displayImage;
        request.send(json);
    }
}

function updateName(){

    var firstName = document.getElementById("first-name").value;
    var lastName = document.getElementById("last-name").value;

    if (firstName && lastName){
        var usersInformation = {first_name : firstName, last_name : lastName};
        var json = JSON.stringify(usersInformation);

        var csrfToken = getCsrfToken();

        var request = new XMLHttpRequest();
        request.open("PATCH", "/api/v1/users/authenticated_user/users_information/");
        request.setRequestHeader("X-CSRFToken", csrfToken);
        request.setRequestHeader("Content-type", "application/json");
        request.send(json);
    }
}

function updateSelfIntroduction(){

    var selfIntroduction = document.getElementById("self-introduction").value;

    if (selfIntroduction){
        var usersInformation = {self_introduction : selfIntroduction}
        var json = JSON.stringify(usersInformation);

        var csrfToken = getCsrfToken();

        var request = new XMLHttpRequest();
        request.open("PATCH", "/api/v1/users/authenticated_user/users_information/");
        request.setRequestHeader("X-CSRFToken", csrfToken);
        request.setRequestHeader("Content-type", "application/json");
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

function displayImage(){
    var response = JSON.parse(this.response);
    var upload = response.detail;

    if (upload == "画像のアップロードに成功しました"){
        var profileImage = document.getElementById("profile-image");
        profileImage.setAttribute("src", dataURL);

    }
}
