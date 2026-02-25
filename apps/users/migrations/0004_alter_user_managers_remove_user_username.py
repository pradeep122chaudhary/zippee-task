import apps.users.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_usertype_user_user_type'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', apps.users.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
