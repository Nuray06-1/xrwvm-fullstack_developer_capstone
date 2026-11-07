from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel

class Command(BaseCommand):
    help = 'Create the course demonstration car catalogue (idempotent)'
    def handle(self, *args, **kwargs):
        for make, name, kind in [('Toyota','Camry','Sedan'),('Toyota','RAV4','SUV'),('Honda','Accord','Sedan'),('Honda','CR-V','SUV'),('Ford','F-150','Truck'),('Ford','Explorer','SUV')]:
            obj, _ = CarMake.objects.get_or_create(name=make, defaults={'description':f'{make} automobiles'})
            CarModel.objects.get_or_create(car_make=obj, name=name, year=2023, defaults={'type':kind})
        self.stdout.write(self.style.SUCCESS('Car catalogue ready'))
