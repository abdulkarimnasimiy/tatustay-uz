from django.core.management.base import BaseCommand
from django.db import transaction

from dormitory.models import Bed, Floor, Room


SIX_BED_ROOM_SUFFIXES = {1, 6, 7, 12}
FLOOR_RANGE = range(2, 10)
ROOM_RANGE = range(1, 13)


class Command(BaseCommand):
    help = "Populate floors, rooms, and beds using the dormitory room layout rules."

    @transaction.atomic
    def handle(self, *args, **options):
        created_floors = 0
        created_rooms = 0
        created_beds = 0
        deleted_beds = 0

        for floor_number in FLOOR_RANGE:
            floor, floor_created = Floor.objects.get_or_create(number=floor_number)
            if floor_created:
                created_floors += 1

            for room_suffix in ROOM_RANGE:
                room_number = f"{floor_number}{room_suffix:02d}"
                room, room_created = Room.objects.get_or_create(floor=floor, number=room_number)
                if room_created:
                    created_rooms += 1

                capacity = 6 if room_suffix in SIX_BED_ROOM_SUFFIXES else 3
                desired_labels = {str(index) for index in range(1, capacity + 1)}
                existing_beds = {bed.label: bed for bed in room.beds.all()}

                for label in sorted(desired_labels, key=int):
                    if label not in existing_beds:
                        Bed.objects.create(room=room, label=label)
                        created_beds += 1

                removable_beds = [
                    bed for label, bed in existing_beds.items()
                    if label not in desired_labels and not bed.is_occupied and not bed.applications.exists()
                ]
                if removable_beds:
                    deleted_beds += len(removable_beds)
                    Bed.objects.filter(pk__in=[bed.pk for bed in removable_beds]).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded dormitory layout: floors+{created_floors}, rooms+{created_rooms}, beds+{created_beds}, beds_removed={deleted_beds}"
        ))
