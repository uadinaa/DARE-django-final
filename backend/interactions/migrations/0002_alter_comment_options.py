# Generated by Django 5.2.1 on 2025-05-12 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("interactions", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
    ]
