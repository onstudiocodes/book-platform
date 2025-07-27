from django.core.management import BaseCommand
from django.db import connection
from silk.models import Request, Profile

class Command(BaseCommand):
    help = 'Clear Silk profiling history and vacuum SQLite database.'

    def handle(self, *args, **options):
        Request.objects.all().delete()
        Profile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Silk history cleared.'))

        # Vacuum SQLite DB to decrease file size
        with connection.cursor() as cursor:
            cursor.execute('VACUUM;')
        self.stdout.write(self.style.SUCCESS('SQLite database vacuumed.'))