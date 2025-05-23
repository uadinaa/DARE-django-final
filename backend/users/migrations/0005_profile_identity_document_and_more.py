# Generated by Django 5.2.1 on 2025-05-14 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_profile_level_score_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="identity_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="verification_documents/identity/",
                verbose_name="Документ (Удостоверение)",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="qualification_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="verification_documents/qualification/",
                verbose_name="Документ (Квалификация)",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="verification_requested_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Время последнего запроса верификации",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="verification_status",
            field=models.CharField(
                choices=[
                    ("none", "Нет заявки"),
                    ("pending", "На рассмотрении"),
                    ("approved", "Одобрено"),
                    ("rejected", "Отклонено"),
                ],
                default="none",
                max_length=10,
                verbose_name="Статус верификации",
            ),
        ),
    ]
