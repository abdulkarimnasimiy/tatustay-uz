from django.core.validators import RegexValidator
from django.db import models


class Floor(models.Model):
	number = models.PositiveSmallIntegerField(unique=True)

	class Meta:
		ordering = ("number",)

	def __str__(self) -> str:
		return f"Floor {self.number}"


class Room(models.Model):
	floor = models.ForeignKey(Floor, on_delete=models.PROTECT, related_name="rooms")
	number = models.CharField(max_length=20)

	class Meta:
		ordering = ("floor__number", "number")
		constraints = [
			models.UniqueConstraint(fields=["floor", "number"], name="unique_room_number_per_floor"),
		]

	def __str__(self) -> str:
		return f"Floor {self.floor.number} / Room {self.number}"


class Bed(models.Model):
	label = models.CharField(
		max_length=10,
		validators=[RegexValidator(regex=r"^[A-Za-z0-9]+$", message="Bed label must be alphanumeric.")],
	)
	room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="beds")
	is_occupied = models.BooleanField(default=False, db_index=True)

	class Meta:
		ordering = ("room__floor__number", "room__number", "label")
		constraints = [
			models.UniqueConstraint(fields=["room", "label"], name="unique_bed_label_per_room"),
		]

	def __str__(self) -> str:
		status = "Occupied" if self.is_occupied else "Available"
		return f"Floor {self.room.floor.number} / Room {self.room.number} / Bed {self.label} ({status})"
