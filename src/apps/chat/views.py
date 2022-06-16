from .event_handlers import send_invite_message

from django.http import HttpResponse

from django.shortcuts import render


def room(request, guild_id):
    return render(request, 'test.html', {
        'guild_id': guild_id
    })


def event(request):
    send_invite_message(1, '123')
    return HttpResponse()
