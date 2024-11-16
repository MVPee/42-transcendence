import time
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from srcs.community.consumers.notificationConsumer import NotificationConsumer

class Command(BaseCommand):
    help = "Send a notification to all connected WebSocket clients"

    def add_arguments(self, parser):
        parser.add_argument(
            '--message', type=str, required=True, help="The notification message to send"
        )
        parser.add_argument(
            '--username', type=str, default='System', help="The username sending the notification"
        )

    def handle(self, *args, **options):
        # Extract arguments
        message = options['message']
        username = options['username']

        # Get the channel layer
        channel_layer = get_channel_layer()

        # Call the send_notification_to_all method
        async_to_sync(NotificationConsumer.send_notification_to_all)(
            channel_layer, message, username=username
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent notification: "{message}" from "{username}".')
        )
