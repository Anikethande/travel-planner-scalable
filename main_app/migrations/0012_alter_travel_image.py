# Generated by Django 4.0.5 on 2024-04-11 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_rename_status_checklist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='image',
            field=models.ImageField(default='images/no-image.png', upload_to='images/'),
        ),
    ]