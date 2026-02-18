from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser admin with default credentials'

    def handle(self, *args, **options):
        # Check if admin user exists and delete it if it does (recreate logic)
        user_exists = User.objects.filter(username='admin').exists()
        if user_exists:
            User.objects.filter(username='admin').delete()
        
        # Create the superuser
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        
        if user_exists:
            self.stdout.write(
                self.style.SUCCESS('Superuser "admin" recreated successfully!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Superuser "admin" created successfully!')
            )
