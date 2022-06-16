from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from apps.translate import views as views_translate
from apps.system import views as views_system
from apps.api import views as views_api


router = DefaultRouter(trailing_slash=False)
router.register('armors', views_api.ArmorCardViewSet, basename='armors')
router.register('cards', views_api.CardViewSet, basename='cards')
router.register('cardtypes', views_api.CardTypeViewSet, basename='cardtypes')
router.register('chests', views_api.ChestViewSet, basename='chests')
router.register('elements', views_api.ElementViewSet, basename='elements')
router.register('guilds', views_api.GuildViewSet, basename='guilds')
router.register('languages', views_translate.LanguageViewSet, basename='languages')
router.register('level', views_api.LevelViewSet, basename='level')
router.register('logs', views_api.ChatLogViewSet, basename='logs')
router.register('players', views_api.PlayerViewSet, basename='players')
router.register('potions', views_api.PotionCardViewSet, basename='potions')
router.register('system_info', views_system.SystemInfoViewSet, basename='system_info')
router.register('tickets', views_api.TicketViewSet, basename='tickets')
router.register('translate', views_translate.TranslateViewSet, basename='translate')
router.register('warriors', views_api.WarriorCardViewSet, basename='warriors')
router.register('weapons', views_api.WeaponCardViewSet, basename='weapons')
router.register('auction', views_api.AuctionLotView, basename='auction')
router.register('battle_log', views_api.BattleLogViewSet, basename='battle_log')

additional_urlpatterns = [
    path('players/cards/<int:pk>', views_api.PlayerViewSet.as_view({'get': 'cards_retrieve'}), name='user-cards')
]

urlpatterns = router.urls
urlpatterns += additional_urlpatterns
