import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Users connect to this socket to receive live updates. The connection
    subscribes them to a personal channel group based on their user ID.
    """

    async def connect(self):
        # The AuthMiddlewareStack parses the session/auth
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            # Group name based on the user's ID
            self.group_name = f"user_notifications_{self.user.id}"

            # Join the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            # Leave the group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        # We don't currently expect clients to send data up this socket,
        # but if they do, we handle it here.
        pass

    async def notify(self, event):
        """
        Handler for the 'notify' event type.
        Sends the payload down to the connected WebSocket client.
        """
        payload = event["payload"]
        await self.send(text_data=json.dumps(payload))
