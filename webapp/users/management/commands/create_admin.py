from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user for the MQTT monitoring system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Admin email')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User "{username}" already exists.')
                    )
                    return

                # Create admin user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='admin',
                    is_staff=True,
                    is_superuser=True
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created admin user "{username}" with role "admin"'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Username: {username}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Password: {password}')
                )
                self.stdout.write(
                    self.style.WARNING('Please change the password after first login!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
