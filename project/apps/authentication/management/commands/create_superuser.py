from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser admin with default credentials'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser "admin" created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser "admin" already exists!')
            )