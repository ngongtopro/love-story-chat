from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from happy_farm.models import Farm, FarmPlot


class Command(BaseCommand):
    help = 'Create farms for existing users who do not have farms'

    def handle(self, *args, **options):
        # Find users without farms
        users_without_farms = User.objects.filter(farm__isnull=True)
        count = users_without_farms.count()
        
        self.stdout.write(f"Found {count} users without farms")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("All users already have farms!"))
            return
        
        # Create farms for users
        created_count = 0
        for user in users_without_farms:
            farm = Farm.objects.create(user=user)
            
            # Create 6 initial plots for each user
            for plot_num in range(6):
                FarmPlot.objects.create(farm=farm, plot_number=plot_num, state='empty')
            
            created_count += 1
            self.stdout.write(f"Created farm and 6 plots for user: {user.username}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created farms for {created_count} users!")
        )