from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views


urlpatterns = [
    path("users/", views.CreateUserView.as_view()),
    path("users/dummy_students/", views.CreateDummyStudentView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("users/<user_id>/", views.GetUserView.as_view()), # ユーザーの詳細情報を取得する
    path("users/authenticated_user/users_information/", views.UpdateUsersInformationView.as_view()), # ユーザーの情報を更新する
    path("users/authenticated_user/profile_image/", views.UpdateProfileImageView.as_view()), # ユーザーのプロフィール画像を更新する
    path("users/authenticated_user/classes/current_class/", views.GetCurrentClassView.as_view()), # ログインユーザーが予約した授業のうち、現在行われている授業を取得する
    path("classes/non_reserved_classes/teachers/", views.GetTeachersView.as_view()), # 授業が予約可能な講師を取得する
    path("users/authenticated_student/classes/daily_classes/", views.GetDailyStudentsReservedClassView.as_view()), # 生徒が予約した、今日行われる残りの授業を取得する
    path("users/authenticated_student/classes/weekly_classes/", views.GetWeeklyStudentsReservedClassView.as_view()), # 一週間分の、生徒が予約した授業を取得する(ただし、現在時刻より前の授業は取得されない)
    path("classes/weekly_classes/", views.GetWeeklySpecificReservedClassView.as_view()), # 一週間分の、特定の生徒が予約した特定の講師の授業を取得する(ただし、現在時刻より前の授業は取得されない)
    path("classes/", views.GetTeachersClassView.as_view()), # 生徒が予約していない、特定のクラスの詳細情報を取得する
    path("classes/<class_id>/", views.AddReservedClassView.as_view()), # 生徒がクラスを予約する
    path("users/authenticated_teacher/classes/daily_classes/reserved_classes/", views.GetDailyTeachersReservedClassView.as_view()), # 講師が今日行う授業のうち、残りの授業を取得する
    path("users/authenticated_teacher/classes/weekly_classes/reserved_classes/", views.GetWeeklyTeachersReservedClassView.as_view()), # 講師の一週間分の、予約された授業を取得する(ただし、現在時刻より前の授業は取得されない)
    path("users/<teacher_id>/classes/weekly_classes/", views.GetWeeklyTeachersClassView.as_view()), # 講師の一週間分の授業を取得する
    path("users/authenticated_teacher/classes/", views.AddTeachersClassView.as_view()), # 講師が授業を登録する
]
