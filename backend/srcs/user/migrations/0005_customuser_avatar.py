# Generated by Django 5.1.2 on 2024-11-09 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_customuser_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='avatars/profile.png', upload_to='avatars/'),
        ),
    ]