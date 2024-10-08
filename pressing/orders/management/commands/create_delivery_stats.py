from django.core.management.base import BaseCommand
from orders.models import CustomUser, DeliveryStats

class Command(BaseCommand):
    help = 'Create DeliveryStats for all delivery users'

    def handle(self, *args, **kwargs):
        delivery_users = CustomUser.objects.filter(role='deliver')
        for user in delivery_users:
            DeliveryStats.objects.get_or_create(delivery_user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created DeliveryStats for all delivery users.'))