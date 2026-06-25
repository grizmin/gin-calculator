from django.core.management.base import BaseCommand
from calculator.models import GinRecipe

class Command(BaseCommand):
    help = 'Delete orphaned recipes with IDs 3, 4, and 5'

    def handle(self, *args, **options):
        # Delete the orphaned recipes
        deleted_count, _ = GinRecipe.objects.filter(id__in=[3, 4, 5]).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} orphaned recipes')
        )