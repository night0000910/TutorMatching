from django.db import models
from django.contrib.auth.models import AbstractUser

import datetime

USER_TYPE = [("teacher", "teacher"), ("student", "student")]
USERS_RANK = [("bronze", "bronze"), ("silver", "silver"), ("gold", "gold"), ("diamond", "diamond")]

class UserModel(AbstractUser):
    user_type = models.TextField(choices=USER_TYPE, default="student") # ユーザーが講師か生徒かを示す
    first_name = models.TextField(default="") # ユーザーの名前
    last_name = models.TextField(default="") # ユーザーの名字
    profile_image = models.ImageField(upload_to="", default="ProfileImage.png")
    account_start_datetime = models.DateTimeField(auto_now_add=True) # アカウントを作成した日付、時刻
    self_introduction = models.TextField(default="")
    spent_time = models.IntegerField(default=0) # 講師の総授業時間 or 生徒の総学習時間
    rank = models.TextField(choices=USERS_RANK, default="bronze")
    class_start_datetime = models.DateTimeField(default=datetime.datetime(2000, 1, 1)) # 最後に授業に参加した日付、時刻
    class_ending_datetime = models.DateTimeField(default=datetime.datetime(2000, 1, 1)) # 最後に授業を終了した日付、時刻

class StudentModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)

class TeacherModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)

class ClassModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, default=1) # 授業を受ける生徒
    teacher = models.ForeignKey(TeacherModel, on_delete=models.CASCADE) # 授業を担当する講師
    datetime = models.DateTimeField() # 授業を開始する日付、時刻