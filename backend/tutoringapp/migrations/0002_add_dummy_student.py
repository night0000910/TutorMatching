from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_dummy_student(apps, schema_editor):
    UserModel = apps.get_model('tutoringapp', 'UserModel')
    StudentModel = apps.get_model('tutoringapp', 'StudentModel')
    
    # UserModelのID: 1 を作成
    user, created = UserModel.objects.get_or_create(
        username='dummy_student',
        defaults={
            'password': make_password(None),
            'is_active': False,
            'first_name': 'student',
            'last_name': 'dummy',
            'user_type': 'student'
        }
    )

    # StudentModelのID: 1 を作成
    StudentModel.objects.get_or_create(user=user)

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