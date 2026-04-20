from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("accounts", "0001_initial"),
	]

	operations = [
		migrations.CreateModel(
			name="StudentProfile",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("first_name", models.CharField(max_length=150)),
				("last_name", models.CharField(max_length=150)),
				("phone", models.CharField(max_length=20)),
				("faculty", models.CharField(max_length=255)),
				("course", models.CharField(max_length=100)),
				(
					"user",
					models.OneToOneField(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="student_profile",
						to="accounts.user",
					),
				),
			],
		),
	]
