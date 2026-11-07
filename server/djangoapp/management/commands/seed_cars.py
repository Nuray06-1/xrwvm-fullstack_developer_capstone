import json
from pathlib import Path
from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel

class Command(BaseCommand):
    help = 'Load every car in the supplied course dataset without deleting existing data'
    def handle(self, *args, **kwargs):
        source = Path(__file__).resolve().parents[3] / 'database/data/car_records.json'
        rows = json.loads(source.read_text())['cars']
        for row in rows:
            make, _ = CarMake.objects.get_or_create(name=row['make'], defaults={'description': row['make'] + ' automobiles'})
            CarModel.objects.get_or_create(car_make=make, name=row['model'], year=row['year'], defaults={'type': row['bodyType']})
        self.stdout.write(self.style.SUCCESS(f'Car catalogue ready: {CarModel.objects.count()} models'))
