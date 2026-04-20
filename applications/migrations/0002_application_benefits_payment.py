from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="benefit_category",
            field=models.CharField(
                choices=[
                    ("none", "No benefit"),
                    ("disability", "Nogironlik"),
                    ("iron_notebook", "Temir daftar"),
                    ("women_notebook", "Ayollar daftari"),
                    ("youth_notebook", "Yoshlar daftari"),
                ],
                db_index=True,
                default="none",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="benefit_document",
            field=models.FileField(blank=True, null=True, upload_to="benefit_documents/"),
        ),
        migrations.AddField(
            model_name="application",
            name="passport_series",
            field=models.CharField(default="AA", max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="application",
            name="passport_number",
            field=models.CharField(default="0000000", max_length=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="application",
            name="passport_pinfl",
            field=models.CharField(default="00000000000000", max_length=14),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="application",
            name="passport_issued_by",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="application",
            name="monthly_price",
            field=models.PositiveIntegerField(default=300000),
        ),
        migrations.AddField(
            model_name="application",
            name="payment_status",
            field=models.CharField(
                choices=[("unpaid", "Unpaid"), ("paid", "Paid")],
                db_index=True,
                default="unpaid",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="payment_reference",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="application",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
