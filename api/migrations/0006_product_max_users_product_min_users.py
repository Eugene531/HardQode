# Generated by Django 5.0.2 on 2024-03-03 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_product_num_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_users',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='product',
            name='min_users',
            field=models.PositiveIntegerField(default=1),
        ),
    ]