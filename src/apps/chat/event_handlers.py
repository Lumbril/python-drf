from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync


def send_invite_message(guild_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{guild_id}",
        {
            'type': 'invite_message',
            'message': message
        }
    )
