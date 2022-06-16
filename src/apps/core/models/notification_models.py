from django.contrib.auth import get_user_model

from django.db import models


UserModel = get_user_model()


class NotificationManager(models.Manager):

    def create_notification(self, user=None, header='test notification', body='test', author='admin'):
        if user is None:
            user_qs = UserModel.objects.filter(username='TESTNOTIFICATION')

            if user_qs.exists():
                user = user_qs.first()
            else:
                user = UserModel()
                user.username = 'TESTNOTIFICATION'
                user.password = 'testtest1234'
                user.save()

        test_notification = Notification()
        test_notification.user = user
        test_notification.header = header
        test_notification.body = body
        test_notification.author = author
        test_notification.save()

        return True


class Notification(models.Model):
    """Уведомление"""

    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    header = models.CharField(max_length=100, null=True, verbose_name='Заголовок')
    body = models.TextField(null=True, verbose_name='Содержание')
    author = models.CharField(max_length=100, null=True, verbose_name='Кто отправил')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    date_departure = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Дата отправки')
    date_reading = models.DateTimeField(null=True, blank=True, verbose_name='Дата прочтения')
    date_edited = models.DateTimeField(null=True, auto_now=True, verbose_name='Дата изменения')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    objects = NotificationManager()

    def __str__(self): return str(self.header)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
