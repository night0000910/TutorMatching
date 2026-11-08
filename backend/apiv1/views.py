from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model, login, logout
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import status, views
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from dateutil.relativedelta import relativedelta

import datetime
import math
import base64
import random
import string

from . import serializers
import tutoringapp.models


# --------------------------------関数-------------------------------


# 行のセットをリストに変換する
def change_set_to_list(record_set):

    record_list = []

    for record in record_set:
        record_list.append(record)
    
    return record_list

# 引数に渡された時刻が、昨日の15時0分(JSTにおける、今日の0時0分)から一週間以内の時刻かどうかを判定する
def judge_datetime_is_within_oneweek(this_datetime):
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    seven_days_after = today + datetime.timedelta(days=7)

    if today <= this_datetime < seven_days_after:
        return True
    else:
        return False

# 重複した時刻の授業を返す
def return_datetime_duplicate_class(class_list, year, month, day, hour):

    duplicate_class = None

    for this_class in class_list:

        if this_class.datetime.year == year and this_class.datetime.month == month and this_class.datetime.day == day and this_class.datetime.hour == hour:
            duplicate_class = this_class
    
    return duplicate_class

# UTCをJSTに変換する
# 引数では、UTCとしての日付、時刻を受け取る
def change_utc_to_jst(year, month, day, hour):

    time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    time += datetime.timedelta(hours=9) # JSTをUTCに変換

    year = time.year
    month = time.month
    day = time.day
    hour = time.hour

    return (year, month, day, hour)

# JSTをUTCに変換する
# 引数では、JSTとしての日付、時刻を受け取る
def change_jst_to_utc(year, month, day, hour):

    time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
    time -= datetime.timedelta(hours=9) # JSTをUTCに変換

    year = time.year
    month = time.month
    day = time.day
    hour = time.hour

    return (year, month, day, hour)

# ISO8601形式の文字列を個別の数字に分解する
# 引数では、JSTとしての日付、時刻を表すISO8601形式の文字列を受け取る
# JSTとしての日付、時刻を戻り値として返す
def divide_iso8601(datetime_text):
    datetime_list = datetime_text.split("T")
    date = datetime_list[0] # 日付を表す文字列
    time = datetime_list[1] # 時刻を表す文字列
    time = time.split("+")[0]

    date_list = date.split("-")
    year = int(date_list[0])
    month = int(date_list[1])
    day = int(date_list[2])

    time_list = time.split(":")
    hour = int(time_list[0])
    minute = int(time_list[1])
    second = math.floor(float(time_list[2]))

    return (year, month, day, hour, minute, second)

# 引数で受け取った日付、時刻が、現在時刻からx時間後より後かどうかを判定する
# hours : xを表す
def judge_datetime_is_x_hours_later(time, hours):
    now = timezone.now().replace(minute=0, second=0, microsecond=0) # UTCにおける現在時刻(ただし、分、秒、マイクロ秒は0)
    x_hours_later = now + datetime.timedelta(hours=hours) # nowの日付、時刻からx時間後

    if time.timestamp() >= x_hours_later.timestamp():
        return True    
    else:
        return False

# UserModelをシリアライズする
def serialize_user(user):

    serializer = serializers.UserSerializer(instance=user)
    user_data = serializer.data
    print(user_data)

    rank = user_data.pop("rank")

    if rank == "bronze":
        rank = "ブロンズ"
    elif rank == "silver":
        rank = "シルバー"
    elif rank == "gold":
        rank = "ゴールド"
    elif rank == "diamond":
        rank = "ダイヤ"
    
    user_data["rank"] = rank

    account_start_datetime_text = user_data.pop("account_start_datetime") # account_start_datetime_text変数には、ISO8601に則って表記されたJSTにおける日時の文字列が格納されている
    year, month, day, hour, minute, second = divide_iso8601(account_start_datetime_text)

    user_data["account_start_year"] = year
    user_data["account_start_month"] = month
    user_data["account_start_day"] = day
    user_data["account_start_hour"] = hour
    user_data["account_start_minute"] = minute
    user_data["account_start_second"] = second

    class_start_datetime_text = user_data.pop("class_start_datetime") # class_start_datetime_text変数には、ISO8601に則って表記されたJSTにおける日時の文字列が格納されている
    year, month, day, hour, minute, second = divide_iso8601(class_start_datetime_text)

    user_data["class_start_year"] = year
    user_data["class_start_month"] = month
    user_data["class_start_day"] = day
    user_data["class_start_hour"] = hour
    user_data["class_start_minute"] = minute
    user_data["class_start_second"] = second

    class_ending_datetime_text = user_data.pop("class_ending_datetime") # class_ending_datetime_text変数には、ISO8601に則って表記されたJSTにおける日時の文字列が格納されている
    year, month, day, hour, minute, second = divide_iso8601(class_ending_datetime_text)

    user_data["class_ending_year"] = year
    user_data["class_ending_month"] = month
    user_data["class_ending_day"] = day
    user_data["class_ending_hour"] = hour
    user_data["class_ending_minute"] = minute
    user_data["class_ending_second"] = second

    if user_data["user_type"] == "teacher":

        jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける現在時刻
        account_start_datetime = datetime.datetime(user_data["account_start_year"], user_data["account_start_month"], user_data["account_start_day"], user_data["account_start_hour"], tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
        elapsed_datetime = relativedelta(jst_today, account_start_datetime)

        if elapsed_datetime.year is not None:
            elapsed_year = f"{elapsed_datetime.year}年"
        else:
            elapsed_year = "1年未満"

        user_data["career"] = elapsed_year
    
    return user_data

# class_list内の授業の中で、今日の0時0分からdays日後の0時0分から、days+1日後の0時0分までの授業を取得する
# x_hours_laterに整数を渡した場合、現在時刻からx_hours_later時間後より前の授業は取得されない
def get_daily_class_list(class_list, days, x_hours_later):
    gotten_class_list = []
    jst_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # JSTにおける現在時刻
    today = timezone.now().replace(day=jst_now.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    zero_oclock = 0
    fifteen_oclock = 15
    twenty_four_oclock = 24

    if type(x_hours_later) == int:
        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=days)
            duplicate_class = return_datetime_duplicate_class(class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and judge_datetime_is_x_hours_later(added_datetime, x_hours_later):
                gotten_class_list.append(duplicate_class)

        for j in range(zero_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=days+1)
            duplicate_class = return_datetime_duplicate_class(class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class and judge_datetime_is_x_hours_later(added_datetime, x_hours_later):
                gotten_class_list.append(duplicate_class)
    
    else:
        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=days)
            duplicate_class = return_datetime_duplicate_class(class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                gotten_class_list.append(duplicate_class)

        for j in range(zero_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=days+1)
            duplicate_class = return_datetime_duplicate_class(class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                gotten_class_list.append(duplicate_class)

    return gotten_class_list

# ClassModelのリストをシリアライズする
def serialize_class_list(class_list):

    serializer = serializers.ClassSerializer(instance=class_list, many=True) # この処理において、UTCはJSTへ変換される
    class_list = serializer.data

    for i, specific_class in enumerate(class_list):

        class_datetime_text = specific_class.pop("datetime") # class_datetime_text変数には、ISO8601に則って表記されたJSTにおける日時の文字列が格納されている
        year, month, day, hour, minute, second = divide_iso8601(class_datetime_text)

        class_list[i]["year"] = year
        class_list[i]["month"] = month
        class_list[i]["day"] = day
        class_list[i]["hour"] = hour

        student_id = specific_class.pop("student") # student_idは、生徒のStudentModelにおけるid
        teacher_id = specific_class.pop("teacher") # teacher_idは、講師のTeacherModelにおけるid

        student = backend.tutoringapp.models.StudentModel.objects.get(id=student_id)
        student = student.user
        student_id = student.id # student_idをUserModelにおけるidに更新
        teacher = backend.tutoringapp.models.TeacherModel.objects.get(id=teacher_id)
        teacher = teacher.user
        teacher_id = teacher.id # teacher_idをUserModelにおけるidに更新

        class_list[i]["student_id"] = student_id
        class_list[i]["teacher_id"] = teacher_id
    
    return class_list

# ランダムなstrインスタンスを生成する
def return_random_str():
   random_str_list = [random.choice(string.ascii_letters + string.digits) for i in range(10)]
   random_str = ''.join(random_str_list)

   now = timezone.now()
   now_str = now.strftime("%Y-%m-%d %H:%M:%S")
   random_str += now_str

   return random_str


# -------------------------講師・生徒共通のAPI-------------------------


class CreateUserView(views.APIView):

    def post(self, request, *args, **kwargs):
        create_user_serializer = serializers.CreateUserSerializer(data=request.data)
        create_user_serializer.is_valid(raise_exception=True)
        user = create_user_serializer.save()

        if user.user_type == "student":
            students_data = {"user" : user.id}
            student_serializer = serializers.StudentSerializer(data=students_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()
        elif user.user_type == "teacher":
            teachers_data = {"user" : user.id}
            teacher_serializer = serializers.TeacherSerializer(data=teachers_data)
            teacher_serializer.is_valid(raise_exception=True)
            teacher_serializer.save()
        
        data = {"detail" : "サインアップに成功しました"}
        
        return Response(data, status.HTTP_200_OK)

class LoginView(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        
        return Response({"detail" : "ログインに成功しました"})

class LogoutView(views.APIView):

    def post(self, request, *args, **kwargs):
        logout(request)

        return Response({"detail" : "ログアウトに成功しました"})

class CreateDummyStudentView(generics.CreateAPIView):
    
    def post(self, request, *args, **kwargs):
        dummy_students_data = {"username" : "dummy_student", "password" : "password", "first_name" : "student", "last_name" : "dummy", "user_type" : "student"}
        create_user_serializer = serializers.CreateUserSerializer(data=dummy_students_data)
        create_user_serializer.is_valid(raise_exception=True)
        user = create_user_serializer.save()

        students_data = {"user" : user.id}
        student_serializer = serializers.StudentSerializer(data=students_data)
        student_serializer.is_valid()
        student_serializer.save()

        data = {"detail" : "dummy_studentの作成に成功しました"}

        return Response(data, status.HTTP_200_OK)

# ユーザーの詳細情報を取得する
class GetUserView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # user_id : ユーザーのUserModelにおけるid
    def get(self, request, user_id, *args, **kwargs):
        user = get_user_model().objects.get(id=user_id)
        user_data = serialize_user(user)

        return Response(user_data, status.HTTP_200_OK)

# ユーザーの情報を更新する
class UpdateUsersInformationView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):

        user = request.user
        data = request.data

        serializer = serializers.UserSerializer(instance=user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail" : "ユーザー情報の更新に成功しました"}, status.HTTP_200_OK)

# ユーザーのプロフィール画像を更新する
class UpdateProfileImageView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):

        user = request.user
        data = request.data
        dataURL = data["file"]
        format, encoded_file_content = dataURL.split(";base64,")
        extension = format.split("/")[-1]
        file_content = base64.b64decode(encoded_file_content)
        file_name = return_random_str()
        file_path = file_name + "." + extension
        file = ContentFile(file_content, name=file_path)
        profile_image = {"profile_image" : file}
        serializer = serializers.UserSerializer(instance=user, data=profile_image, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail" : "画像のアップロードに成功しました"}, status.HTTP_200_OK)

# ログインユーザーが予約した授業のうち、現在行われている授業を取得する
class GetCurrentClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        user = request.user
        now = timezone.now().replace(minute=0, second=0, microsecond=0) # UTCにおける現在時刻(ただし、分、秒、マイクロ秒は0)

        if user.user_type == "student":
            student = backend.tutoringapp.models.StudentModel.objects.get(user=user.id)
            current_class = backend.tutoringapp.models.ClassModel.objects.filter(student=student.id).filter(datetime=now)

        elif user.user_type == "teacher":
            teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=user.id)
            current_class = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).filter(datetime=now)

        serializer = serializers.ClassSerializer(instance=current_class, many=True)

        return Response(serializer.data, status.HTTP_200_OK)


# ---------------------------生徒専用のAPI----------------------------


# 授業が予約可能な講師を取得する
# UserModelのid=1の行は、ダミーの生徒を表している
class GetTeachersView(views.APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teachers_set = backend.tutoringapp.models.TeacherModel.objects.all()
        teachers_list = []

        for teacher in teachers_set:
            teachers_class_set = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id)

            for teachers_class in teachers_class_set:

                if judge_datetime_is_within_oneweek(teachers_class.datetime) and judge_datetime_is_x_hours_later(teachers_class.datetime, 2) and teachers_class.student.user.id == 1: # ClassModelにおいてstudent列の値が1(ダミーの生徒)の授業は、予約されていない授業を表す
                    teacher = teacher.user # TeacherModelからUserModelへ変換
                    teachers_list.append(teacher)
                    break
        
        serializer = serializers.UserSerializer(instance=teachers_list, many=True)
        teachers_list = serializer.data

        return Response(teachers_list, status.HTTP_200_OK)

# 生徒が予約した、今日行われる残りの授業を取得する
class GetDailyStudentsReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, *args, **kwargs):

        user = request.user
        student = backend.tutoringapp.models.StudentModel.objects.get(user=user.id)

        reserved_class_set = backend.tutoringapp.models.ClassModel.objects.filter(student=student.id) # 特定の生徒が予約した授業のセット
        reserved_class_list = change_set_to_list(reserved_class_set)
        daily_reserved_class_list = get_daily_class_list(reserved_class_list, 0, 0)

        daily_reserved_class_list = serialize_class_list(daily_reserved_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(daily_reserved_class_list, status.HTTP_200_OK) # 日付、時刻はJSTとして返す

# 一週間分の、生徒が予約した授業を取得する(ただし、現在時刻より前の授業は取得されない)
class GetWeeklyStudentsReservedClassView(views.APIView):
    
    permission_class = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        student = backend.tutoringapp.models.StudentModel.objects.get(user=user.id)

        reserved_class_set = backend.tutoringapp.models.ClassModel.objects.filter(student=student.id)
        reserved_class_list = change_set_to_list(reserved_class_set)
        weekly_reserved_class_list = []

        zero_days_after = 0
        seven_days_after = 7

        for i in range(zero_days_after, seven_days_after):

            daily_reserved_class_list = get_daily_class_list(reserved_class_list, i, 0)

            for daily_reserved_class in daily_reserved_class_list:
                weekly_reserved_class_list.append(daily_reserved_class)

        weekly_reserved_class_list = serialize_class_list(weekly_reserved_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(weekly_reserved_class_list, status.HTTP_200_OK) # 日付、時刻はJSTとして返す


# 一週間分の、特定の生徒が予約した特定の講師の授業を取得する(ただし、現在時刻から2時間後より前の授業は取得されない)
class GetWeeklySpecificReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, *args, **kwargs):
        teacher_id = request.query_params.get("teacher_id")
        student_id = request.query_params.get("student_id")

        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=teacher_id)
        student = backend.tutoringapp.models.StudentModel.objects.get(user=student_id)

        reserved_class_set = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).filter(student=student.id) # 講師の授業のうち、特定の生徒が予約した授業のセット
        reserved_class_list = change_set_to_list(reserved_class_set)
        weekly_reserved_class_list = []

        zero_days_after = 0
        seven_days_after = 7

        for i in range(zero_days_after, seven_days_after):

            daily_reserved_class_list = get_daily_class_list(reserved_class_list, i, 2)

            for daily_reserved_class in daily_reserved_class_list:
                weekly_reserved_class_list.append(daily_reserved_class)

        weekly_reserved_class_list = serialize_class_list(weekly_reserved_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(weekly_reserved_class_list, status.HTTP_200_OK) # 日付、時刻はJSTとして返す

# 生徒が予約していない、特定のクラスの詳細情報を取得する
# 講師id, 日付、時刻からクラスを特定する
class GetTeachersClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        teacher_id = request.query_params.get("teacher_id") # 講師のUserModelにおけるid
        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=teacher_id)

        year = int(request.query_params.get("year")) # JSTとして日時を取得する
        month = int(request.query_params.get("month"))
        day = int(request.query_params.get("day"))
        hour = int(request.query_params.get("hour"))

        year, month, day, hour = change_jst_to_utc(year, month, day, hour)
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)

        teachers_class = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).get(datetime=time)
        serializer = serializers.ClassSerializer(instance=teachers_class)

        return Response(serializer.data, status.HTTP_200_OK)

# 生徒がクラスを予約する
class AddReservedClassView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    def patch(self, request, class_id, *args, **kwargs):

        user = request.user
        student = backend.tutoringapp.models.StudentModel.objects.get(user=user.id)

        teachers_class = get_object_or_404(backend.tutoringapp.models.ClassModel, id=class_id)
        serializer = serializers.ClassSerializer(instance=teachers_class, data={"student" : student.id}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)


# ---------------------------講師関連のAPI----------------------------


# 講師が今日行う授業のうち、残りの授業を取得する
class GetDailyTeachersReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).exclude(student=1)
        teachers_class_list = change_set_to_list(teachers_class_set)
        daily_teachers_class_list = get_daily_class_list(teachers_class_list, 0, 0)
        
        daily_teachers_class_list = serialize_class_list(daily_teachers_class_list) # この処理において、UTCはJSTへ変換される

        return Response(daily_teachers_class_list, status.HTTP_200_OK)

# 講師の一週間分の、予約された授業を取得する(ただし、現在時刻より前の授業は取得されない)
class GetWeeklyTeachersReservedClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=user.id)

        teachers_class_set = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id).exclude(student=1)
        teachers_class_list = change_set_to_list(teachers_class_set)
        weekly_teachers_class_list = []

        zero_days_after = 0
        seven_days_after = 7

        for i in range(zero_days_after, seven_days_after):
            
            daily_teachers_class_list = get_daily_class_list(teachers_class_list, i, 0)

            for daily_teachers_class in daily_teachers_class_list:
                weekly_teachers_class_list.append(daily_teachers_class)
        
        weekly_teachers_class_list = serialize_class_list(weekly_teachers_class_list) # この処理において、UTCはJSTへ変換される

        return Response(weekly_teachers_class_list, status.HTTP_200_OK)


# 講師の一週間分の授業を取得する
class GetWeeklyTeachersClassView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    # teacher_id : 講師のUserModelにおけるid, student_id : 生徒のUserModelにおけるid
    def get(self, request, teacher_id, *args, **kwargs):

        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=teacher_id)
        
        teachers_class_set = backend.tutoringapp.models.ClassModel.objects.filter(teacher=teacher.id) # 講師が登録した全ての授業のセット
        teachers_class_list = change_set_to_list(teachers_class_set)
        weekly_teachers_class_list = []

        zero_days_after = 0
        seven_days_after = 7

        for i in range(zero_days_after, seven_days_after):

            daily_teachers_class_list = get_daily_class_list(teachers_class_list, i, False)

            for daily_teachers_class in daily_teachers_class_list:
                weekly_teachers_class_list.append(daily_teachers_class)    

        weekly_teachers_class_list = serialize_class_list(weekly_teachers_class_list) # この処理において、UTCはJSTへ変換される
        
        return Response(weekly_teachers_class_list, status.HTTP_200_OK)

# 講師が授業を登録する
class AddTeachersClassView(views.APIView):

    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        user = request.user
        teacher = backend.tutoringapp.models.TeacherModel.objects.get(user=user.id)
        year = int(request.data.get("year")) # JSTとして日時を取得する
        month = int(request.data.get("month"))
        day = int(request.data.get("day"))
        hour = int(request.data.get("hour"))

        year, month, day, hour = change_jst_to_utc(year, month, day, hour)
        time = datetime.datetime(year, month, day, hour, tzinfo=datetime.timezone.utc)
        time_text = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        serializer = serializers.ClassSerializer(data={"student" : 1, "teacher" : teacher.id, "datetime" : time_text})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)

