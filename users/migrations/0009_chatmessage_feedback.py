# Generated by Django 3.2.15 on 2024-04-12 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_chatmessage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='feedback',
            field=models.CharField(blank=True, choices=[('helpful', 'helpful'), ('not_helpful', 'not_helpful')], max_length=50, null=True),
        ),
    ]