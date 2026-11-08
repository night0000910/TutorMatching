from django.shortcuts import render
from django.shortcuts import render, redirect

import tutoringapp 


# -------------------------講師・生徒共通のページ-------------------------


# ホームページ
def home_page_view(request):
    
    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "home_page.html")

# サインアップページ
def signup_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return render(request, "signup.html")

# サインアップに成功したことを知らせるページ
def succeed_in_signup_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return render(request, "succeed_in_signup.html")

# ログインページ
def login_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "login.html")

def logout_view(request):

    if request.user.is_authenticated:
        return render(request, "logout.html")
    
    else:
        return redirect("home_page")

# ユーザーのプロフィールを表示する
# profile_user_id : プロフィールを表示するユーザーの、UserModelにおけるid
def profile_view(request, profile_user_id):

    if request.user.is_authenticated:
        return render(request, "profile.html", {"profile_user_id" : profile_user_id})

    else:
        return redirect("home_page")

# アカウントを設定する
def setup_account_view(request):

    if request.user.is_authenticated:
        return render(request, "setup_account.html")
    
    else:
        return redirect("home_page")

# 個別指導ページ
def tutoring_view(request):

    if request.user.is_authenticated:
        return render(request, "tutoring.html")
    
    else:
        return redirect("home_page")


# ---------------------------生徒専用のページ----------------------------


# 授業が予約可能な講師を表示する
def reserve_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return render(request, "reserve.html")
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return redirect("home_page")

# 講師の、予約可能な授業を表示する
def choose_reserved_class_datetime_view(request, teacher_id):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return render(request, "choose_reserved_class_datetime.html", {"teacher_id" : teacher_id})
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return redirect("home_page")

# 授業を予約するかどうかを確認
def add_reserved_class_view(request, teacher_id, year, month, day, hour):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return render(request, "add_reserved_class.html", {"teacher_id" : teacher_id, "year" : year, "month" : month, "day" : day, "hour" : hour})
        
        elif user.user_type == "teacher":
            return redirect("manage_schedule")
    
    else:

        return redirect("home_page")


# ---------------------------講師専用のページ----------------------------


# 今日行う予定の授業を表示
# 一週間分の授業の予約画面を表示
def manage_schedule_view(request):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return render(request, "manage_schedule.html")
    
    else:

        return redirect("home_page")

# スケジュールを更新する
def add_teachers_class_view(request, year, month, day, hour):

    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")
        
        elif user.user_type == "teacher":
            return render(request, "add_teachers_class.html", {"year" : year, "month" : month, "day" : day, "hour" : hour})
    
    else:

        return redirect("home_page")