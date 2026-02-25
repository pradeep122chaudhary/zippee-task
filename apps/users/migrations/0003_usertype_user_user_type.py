
import django.db.models.deletion
from django.db import migrations, models


def seed_user_types_and_assign_defaults(apps, schema_editor):
    User = apps.get_model("users", "User")
    UserType = apps.get_model("users", "UserType")

    seeded_roles = [
        {"code": "user", "name": "User", "description": "Default application user."},
        {"code": "staff", "name": "Staff", "description": "Internal staff member."},
        {"code": "admin", "name": "Admin", "description": "Administrative user with elevated access."},
        {
            "code": "super_admin",
            "name": "Super Admin",
            "description": "Full administrative control including superuser access.",
        },
    ]

    role_map = {}
    for role in seeded_roles:
        role_obj, _ = UserType.objects.get_or_create(
            code=role["code"],
            defaults={"name": role["name"], "description": role["description"]},
        )
        fields_to_update = []
        if role_obj.name != role["name"]:
            role_obj.name = role["name"]
            fields_to_update.append("name")
        if role_obj.description != role["description"]:
            role_obj.description = role["description"]
            fields_to_update.append("description")
        if fields_to_update:
            role_obj.save(update_fields=fields_to_update)
        role_map[role["code"]] = role_obj

    for user in User.objects.filter(user_type__isnull=True):
        if user.is_superuser:
            user.user_type = role_map["super_admin"]
        elif user.is_staff:
            user.user_type = role_map["admin"]
        else:
            user.user_type = role_map["user"]
        user.save(update_fields=["user_type"])


def unseed_user_types_and_clear_defaults(apps, schema_editor):
    User = apps.get_model("users", "User")
    UserType = apps.get_model("users", "UserType")

    User.objects.update(user_type=None)
    UserType.objects.filter(code__in=["user", "staff", "admin", "super_admin"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_address_user_bio_user_city_user_country_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(choices=[('user', 'User'), ('staff', 'Staff'), ('admin', 'Admin'), ('super_admin', 'Super Admin')], max_length=32, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='users.usertype'),
        ),
        migrations.RunPython(seed_user_types_and_assign_defaults, unseed_user_types_and_clear_defaults),
    ]
