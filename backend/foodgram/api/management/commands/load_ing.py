from django.core.management.base import BaseCommand
from core.models import Ingredient
import json


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def handle(self, *args, **options):
        with open('ingredients.json', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            ingredient = Ingredient(
                name=item['name'], measurement_unit=item['measurement_unit'])
            ingredient.save()

        self.stdout.write(
            self.style.SUCCESS('Ingredients loaded successfully'))
