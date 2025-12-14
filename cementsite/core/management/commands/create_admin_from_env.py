import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create or update a Django superuser from environment variables."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(self.style.ERROR(
                "ADMIN_PASSWORD is not set; skipping admin creation."))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email}
        )

        # Always ensure email is current and user is superuser/staff
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{username}' created."))
        else:
            self.stdout.write(self.style.WARNING(
                f"Superuser '{username}' updated."))
