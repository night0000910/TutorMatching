from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_dummy_student(apps, schema_editor):
    UserModel = apps.get_model('tutoringapp', 'UserModel')
    StudentModel = apps.get_model('tutoringapp', 'StudentModel')
    
    # UserModelのID: 1 を作成
    if not UserModel.objects.filter(id=1).exists():
        user = UserModel.objects.create(
            id=1,
            username='dummy_student',
            password=make_password(None),  # ログイン不可能なパスワードを設定
            is_active=False,
            first_name='student',
            last_name='dummy',
            user_type='student'
        )
    else:
        user = UserModel.objects.get(id=1)

    # StudentModelのID: 1 を作成
    if not StudentModel.objects.filter(user=user).exists():
        StudentModel.objects.create(
            id=1,
            user=user
        )

def reverse_dummy_student(apps, schema_editor):
    # ロールバック用の処理
    StudentModel = apps.get_model('tutoringapp', 'StudentModel')
    UserModel = apps.get_model('tutoringapp', 'UserModel')
    
    StudentModel.objects.filter(id=1).delete()
    UserModel.objects.filter(id=1).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('tutoringapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_dummy_student, reverse_code=reverse_dummy_student),
    ]