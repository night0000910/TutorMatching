from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path("home_page/", views.home_page_view, name="home_page"),
    path("signup/", views.signup_view, name="signup"),
    path("succeed_in_signup/", views.succeed_in_signup_view, name="succeed_in_signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/<int:profile_user_id>/", views.profile_view, name="profile"),
    path("setup_account/", views.setup_account_view, name="setup_account"),
    path("tutoring/", views.tutoring_view, name="tutoring"),
    path("reserve/", views.reserve_view, name="reserve"),
    path("choose_reserved_class_datetime/<int:teacher_id>/", views.choose_reserved_class_datetime_view, name="choose_reserved_class_datetime"),
    path("add_reserved_class/<int:teacher_id>/<int:year>/<int:month>/<int:day>/<int:hour>/", views.add_reserved_class_view, name="add_reserved_class"),
    path("manage_schedule/", views.manage_schedule_view, name="manage_schedule"),
    path("add_teachers_class/<int:year>/<int:month>/<int:day>/<int:hour>/", views.add_teachers_class_view, name="add_teachers_class"),
]