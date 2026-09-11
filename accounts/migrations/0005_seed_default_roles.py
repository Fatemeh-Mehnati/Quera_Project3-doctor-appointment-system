from django.db import migrations


def seed_default_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")

    roles = [
        ("PATIENT", "Patient"),
        ("DOCTOR", "Doctor"),
        ("ADMIN", "Admin"),
    ]

    for code, name in roles:
        Role.objects.get_or_create(
            code=code,
            defaults={"name": name},
        )


def remove_default_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")

    Role.objects.filter(
        code__in=["PATIENT", "DOCTOR", "ADMIN"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_role_userrole_user_roles_and_more"),
    ]

    operations = [
        migrations.RunPython(
            seed_default_roles,
            remove_default_roles,
        ),
    ]