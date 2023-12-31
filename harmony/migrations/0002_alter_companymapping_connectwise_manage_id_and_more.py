# Generated by Django 4.2.4 on 2023-11-23 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harmony', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companymapping',
            name='connectwise_manage_id',
            field=models.IntegerField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='companymapping',
            name='dynamics365_company_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
