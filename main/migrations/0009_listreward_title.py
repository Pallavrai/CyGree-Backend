# Generated by Django 5.1.2 on 2024-10-28 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_rename_incentive_listreward_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listreward',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
