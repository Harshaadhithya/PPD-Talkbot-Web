# Generated by Django 3.2.15 on 2024-03-15 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_chatsession_updated_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatsession',
            options={'ordering': ['-updated_at']},
        ),
    ]
