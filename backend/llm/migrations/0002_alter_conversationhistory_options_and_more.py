# Generated by Django 5.2.1 on 2025-05-12 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("llm", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="conversationhistory",
            options={"ordering": ["-timestamp"]},
        ),
        migrations.AddField(
            model_name="conversationhistory",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="conversationhistory",
            index=models.Index(fields=["user"], name="llm_convers_user_id_6ab4ac_idx"),
        ),
    ]
