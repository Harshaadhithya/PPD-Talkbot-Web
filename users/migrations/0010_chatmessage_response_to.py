# Generated by Django 3.2.15 on 2024-04-13 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_chatmessage_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='response_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='users.chatmessage'),
        ),
    ]
