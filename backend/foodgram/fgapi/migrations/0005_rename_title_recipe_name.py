# Generated by Django 3.2.18 on 2023-03-11 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fgapi', '0004_auto_20230311_2216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='title',
            new_name='name',
        ),
    ]
