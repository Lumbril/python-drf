from rest_framework import serializers

from apps.chat.models import ChatLog


class ChatLogSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.ranks = dict()
        super().__init__(*args, **kwargs)

    user = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    def get_user(self, obj):
        return dict(
            username=obj.user.username,
            icon=obj.user.get_icon()
        )

    def get_rank(self, obj):
        user = obj.user
        if not self.ranks.get(str(user), False):
            player = user.guild_player.first()
            self.ranks[str(user)] = player.rank.name

        return self.ranks.get(str(user), False)

    class Meta:
        model = ChatLog
        exclude = ('id', 'guild')
