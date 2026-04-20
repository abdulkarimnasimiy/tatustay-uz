from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Floor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveSmallIntegerField(unique=True)),
            ],
            options={
                "ordering": ("number",),
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=20)),
                (
                    "floor",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rooms", to="dormitory.floor"),
                ),
            ],
            options={
                "ordering": ("floor__number", "number"),
                "constraints": [
                    models.UniqueConstraint(fields=("floor", "number"), name="unique_room_number_per_floor")
                ],
            },
        ),
        migrations.CreateModel(
            name="Bed",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "label",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Bed label must be alphanumeric.",
                                regex="^[A-Za-z0-9]+$",
                            )
                        ],
                    ),
                ),
                ("is_occupied", models.BooleanField(db_index=True, default=False)),
                (
                    "room",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="beds", to="dormitory.room"),
                ),
            ],
            options={
                "ordering": ("room__floor__number", "room__number", "label"),
                "constraints": [
                    models.UniqueConstraint(fields=("room", "label"), name="unique_bed_label_per_room")
                ],
            },
        ),
    ]
