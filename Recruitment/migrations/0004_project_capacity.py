# Generated by Django 5.2 on 2025-05-15 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Recruitment', '0003_employer_full_name_alter_jobseeker_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='capacity',
            field=models.IntegerField(default=1),
        ),
    ]
