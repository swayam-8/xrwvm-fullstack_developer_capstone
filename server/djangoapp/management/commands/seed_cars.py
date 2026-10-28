import json
from pathlib import Path
from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel
class Command(BaseCommand):
    help = 'Load the supplied car catalog without duplicating existing records'
    def handle(self, *args, **options):
        path = Path(__file__).resolve().parents[3] / 'database/data/car_records.json'
        for car in json.loads(path.read_text())['cars']:
            make, _ = CarMake.objects.get_or_create(name=car['make'], defaults={'description': f"Vehicles manufactured by {car['make']}"})
            CarModel.objects.get_or_create(car_make=make, name=car['model'], year=car['year'], defaults={'type': car['bodyType']})
        # Keep the original course example models available alongside the supplied inventory.
        example_models = {'Nissan':['Qashqai','XTRAIL'], 'Mercedes':['A-Class','C-Class','E-Class'], 'Audi':['A4','A5','A6'], 'Kia':['Sorrento','Carnival','Cerato'], 'Toyota':['Corolla','Camry','Kluger']}
        for manufacturer, names in example_models.items():
            make, _ = CarMake.objects.get_or_create(name=manufacturer, defaults={'description':f'Vehicles manufactured by {manufacturer}'})
            for name in names:
                CarModel.objects.get_or_create(car_make=make,name=name,year=2023,defaults={'type':'Sedan'})
        self.stdout.write(f'Loaded {CarMake.objects.count()} makes and {CarModel.objects.count()} models')
