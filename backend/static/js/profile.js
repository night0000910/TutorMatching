$(document).ready(function() {
    $('.collapsible').collapsible();

    var profileUserId = document.getElementById("profile-user-id").getAttribute("value");

    var request = new XMLHttpRequest();
    request.open("GET", "/api/v1/users/" + profileUserId + "/");
    request.onload = createElementsOfProfile;
    request.send();
})

function createElementsOfProfile(){
    var response = JSON.parse(this.response);
    console.log(response);

    var userId = document.getElementById("user-id").getAttribute("value");
    var profileUserId = response.id;
    var firstName = response.first_name;
    var lastName = response.last_name;
    var profileImageURL = response.profile_image;
    var userType = response.user_type;
    var selfIntroduction = response.self_introduction;
    var spentTime = response.spent_time;
    var accountStartYear = response.account_start_year;
    var accountStartMonth = response.account_start_month;
    var accountStartDay = response.account_start_day;
    var accountStartHour = response.account_start_hour;
    var rank = response.rank;

    if (rank == "ブロンズ"){
        rank = '<span style="color : #BC9E69;">ブロンズ</span>';
    } else if(rank == "シルバー"){
        rank = '<span style="color : #BEC1C3;">シルバー</span>';
    } else if(rank == "ゴールド"){
        rank = '<span style="color : #EFC986;">ゴールド</span>';
    } else if(rank == "ダイヤ"){
        rank = '<span style="color : #94D1C8;">ダイヤ</span>';
    }

    var profileName = document.getElementById("profile-name");
    var profileImage = document.getElementById("profile-image");
    var profileContent = document.getElementById("profile-content");

    profileName.innerHTML = lastName + " " + firstName;
    profileImage.setAttribute("src", profileImageURL);

    if (userId == profileUserId){ /* 認証済みユーザーのプロフィールを表示する場合 */

        if (userType == "student"){
            var rankElement = document.createElement("h6");
            rankElement.innerHTML = "ランク : " + rank;
            var spentTimeElement = document.createElement("h6");
            spentTimeElement.innerHTML = "総学習時間 : " + spentTime + "分";
            var accountStartDatetimeElement = document.createElement("h6");
            accountStartDatetimeElement.innerHTML = "開始日 : " + accountStartYear + "年 " + accountStartMonth + "月" + accountStartDay + "日";

            profileContent.appendChild(rankElement);
            profileContent.appendChild(spentTimeElement);
            profileContent.appendChild(accountStartDatetimeElement);

            displayReservedClass(userType);

        } else if (userType == "teacher"){
            var rankElement = document.createElement("h6");
            rankElement.innerHTML = "ランク : " + rank;
            var spentTimeElement = document.createElement("h6");
            spentTimeElement.innerHTML = "総授業時間 : " + spentTime + "分";
            var accountStartDatetimeElement = document.createElement("h6");
            accountStartDatetimeElement.innerHTML = "開始日 : " + accountStartYear + "年 " + accountStartMonth + "月" + accountStartDay + "日";

            profileContent.appendChild(rankElement);
            profileContent.appendChild(spentTimeElement);
            profileContent.appendChild(accountStartDatetimeElement);

            displayReservedClass(userType);
        }

    } else{ /* 認証済みでないユーザーのプロフィールを表示する場合 */

        if (userType == "student"){
            var rankElement = document.createElement("h6");
            rankElement.innerHTML = "ランク : " + rank;
            var selfIntroductionElement = document.createElement("h6");
            selfIntroductionElement.innerHTML = selfIntroduction;

            profileContent.appendChild(rankElement);
            profileContent.appendChild(selfIntroductionElement);

        } else if (userType == "teacher"){
            var career = response.career;

            var rankElement = document.createElement("h6");
            rankElement.innerHTML = "ランク : " + rank;
            var careerElement = document.createElement("h6");
            careerElement.innerHTML = "経歴 : " + career
            var selfIntroductionElement = document.createElement("h6");
            selfIntroductionElement.innerHTML = selfIntroduction;

            profileContent.appendChild(rankElement);
            profileContent.appendChild(careerElement);
            profileContent.appendChild(selfIntroductionElement);
        }
    }
}

function displayReservedClass(userType){

    var request = new XMLHttpRequest();

    if (userType == "student"){
        request.open("GET", "/api/v1/users/authenticated_student/classes/weekly_classes/");

    } else if(userType == "teacher"){
        request.open("GET", "/api/v1/users/authenticated_teacher/classes/weekly_classes/reserved_classes/");

    }

    request.onload = createElementsOfReservedClass;
    request.send();
}

function createElementsOfReservedClass(){
    var response = JSON.parse(this.response);
    var reservedClassArray = response;
    sortClassArray(reservedClassArray);
    var dateArray = createDateArray(reservedClassArray);
    console.log(reservedClassArray);
    console.log(dateArray);


    if (reservedClassArray.length >= 1){
        var section = document.createElement("div");
        section.setAttribute("class", "section");
        var h5 = document.createElement("h5");
        h5.innerHTML = "予約した授業";
        var ul = document.createElement("ul");
        ul.setAttribute("class", "collapsible");
        var container = document.getElementById("container");
        
        section.appendChild(h5);
        section.appendChild(ul);
        container.appendChild(section);


        for (date of dateArray){
            var li = document.createElement("li");
            var collapsibleHeader = document.createElement("div");
            collapsibleHeader.setAttribute("class", "collapsible-header");
            collapsibleHeader.innerHTML = '<i class="material-icons">create</i>' + date.month + "月" + date.day + "日"
            var collapsibleBody = document.createElement("div");
            collapsibleBody.setAttribute("class", "collapsible-body");
            var collection = document.createElement("div");
            collection.setAttribute("class", "collection");
            collection.setAttribute("id", date.year + "-" + date.month + "-" + date.day);

            li.appendChild(collapsibleHeader);
            li.appendChild(collapsibleBody);
            collapsibleBody.appendChild(collection);

            ul.appendChild(li);
        }
        
        console.log(ul);

        for (var reservedClass of reservedClassArray){
            var a = document.createElement("a");
            a.setAttribute("class", "collection-item");
            a.setAttribute("href", "#");
            a.innerHTML = reservedClass.hour + ":00";

            var div = document.getElementById(reservedClass.year + "-" + reservedClass.month + "-" + reservedClass.day);
            div.appendChild(a);
        }

        $('.collapsible').collapsible();
    }
}

function sortClassArray(classArray){
    classArray.sort(function (x, y){
        x = new Date(x.year, x.month, x.day, x.hour);
        y = new Date(y.year, y.month, y.day, y.hour);

        return x.getTime() - y.getTime()
    });
}

/* datetimeArrayには、日付時刻が早い順に並べ替えられたDateオブジェクトのArrayオブジェクトを渡す必要がある */
function createDateArray(datetimeArray){
    var dateArray = new Array(datetimeArray[0]);

    for (var i = 1; i <= (datetimeArray.length-1); i++){

        var x = datetimeArray[i];
        var y = datetimeArray[i-1];

        if (!(x.year == y.year && x.month == y.month && x.day == y.day)){
            dateArray.push(datetimeArray[i]);
        }
    }

    return dateArray;
}