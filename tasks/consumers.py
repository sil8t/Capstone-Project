from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AppConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Only allow authenticated users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Join user-specific channel group (used for invites)
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # If a team_id is provided in the URL, join the team-specific group
        self.team_id = self.scope['url_route']['kwargs'].get('team_id')
        if self.team_id:
            self.team_group = f"team_{self.team_id}"
            await self.channel_layer.group_add(self.team_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Cleanly leave any subscribed groups on disconnect
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, "team_group"):
            await self.channel_layer.group_discard(self.team_group, self.channel_name)

    async def receive(self, text_data):
        # No client-to-server messaging required yet
        pass

    async def task_event(self, event):
        # Broadcast task updates to team members
        await self.send(text_data=json.dumps(event))

    async def invite_event(self, event):
        # Notify invited user of a new team invite
        await self.send(text_data=json.dumps(event))
