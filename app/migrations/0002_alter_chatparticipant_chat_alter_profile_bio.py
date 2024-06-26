# Generated by Django 5.0.6 on 2024-06-14 06:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatparticipant',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.chat'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, max_length=100),
        ),
    ]
