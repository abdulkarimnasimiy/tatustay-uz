from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("accounts", "0002_studentprofile"),
	]

	operations = [
		migrations.AddField(
			model_name="studentprofile",
			name="distance_km",
			field=models.PositiveSmallIntegerField(default=0),
		),
		migrations.AddField(
			model_name="studentprofile",
			name="distance_level",
			field=models.CharField(
				choices=[
					("near", "Yaqin"),
					("medium", "O'rtacha"),
					("far", "Uzoq"),
					("very_far", "Juda uzoq"),
				],
				default="near",
				max_length=20,
			),
		),
		migrations.AddField(
			model_name="studentprofile",
			name="region",
			field=models.CharField(
				choices=[
					("tashkent_city", "Toshkent shahri"),
					("tashkent_region", "Toshkent viloyati"),
					("sirdaryo", "Sirdaryo"),
					("jizzakh", "Jizzax"),
					("namangan", "Namangan"),
					("andijan", "Andijon"),
					("fargona", "Farg'ona"),
					("samarkand", "Samarqand"),
					("navoi", "Navoiy"),
					("bukhara", "Buxoro"),
					("qashqadaryo", "Qashqadaryo"),
					("surxondaryo", "Surxondaryo"),
					("khorezm", "Xorazm"),
					("republic_of_karakalpakstan", "Qoraqalpog'iston Respublikasi"),
				],
				default="tashkent_city",
				max_length=40,
			),
		),
	]
