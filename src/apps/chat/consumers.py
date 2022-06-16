from channels.generic.websocket import AsyncWebsocketConsumer

from channels.db import database_sync_to_async

from django.utils import timezone, dateformat

from .service import get_user_by_token

from apps.core.models import Guild

from .models import ChatLog

import json


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.guild_id = None
        self.room_group_name = None
        self.user = None

    async def connect(self):
        self.guild_id = self.scope['url_route']['kwargs']['guild_id']
        self.room_group_name = 'chat_%s' % self.guild_id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        token = self.scope['subprotocols']
        token = token[0] if token else None
        self.user = await database_sync_to_async(get_user_by_token)(token)
        if await self._is_guild_member():
            await self.accept(token)
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if not message:
            return
        current_time = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        await self.chat_log_write(user_id=self.user.id, message=message, time=current_time)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'icon': self.user.icon,
                'rank': await self.get_user_rank(),
                'time': current_time
            }
        )

    @database_sync_to_async
    def _is_guild_member(self):
        if not Guild.objects.filter(id=self.guild_id).exists():
            return False
        guild = Guild.objects.get(id=self.guild_id)
        if self.user.id in [guild_player.player.id for guild_player in guild.players.all()]:
            return True
        return False

    @database_sync_to_async
    def get_user_rank(self):
        return self.user.guild_player.first().rank.name if self.user.guild_player.first().rank else None

    @database_sync_to_async
    def chat_log_write(self, user_id, message, time):
        new_message = ChatLog(guild_id=self.guild_id, user_id=user_id, message=message, time=time)
        new_message.save()

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'time': event['time'],
            'user': {'username': event['username'], 'icon': event['icon']},
            'rank': event['rank']
        }))

    async def invite_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
