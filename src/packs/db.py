from django.db import models


class Count(models.Subquery):

    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


def rename_tables() -> None:

    from rest_framework.authtoken.models import Token, TokenProxy
    from django.db.migrations.recorder import MigrationRecorder
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Group, Permission
    from django.contrib.sessions.models import Session
    from django.contrib.admin.models import LogEntry

    '''Init Migration class'''
    MigrationRecorder.Migration()

    '''Edit db_table of Token model'''
    Token._meta.db_table = 'tokens'
    Token._meta.original_attrs['db_table'] = 'tokens'

    '''Edit db_table of TokenProxy model'''
    TokenProxy._meta.db_table = 'tokens'
    TokenProxy._meta.original_attrs['db_table'] = 'tokens'

    '''Edit db_table in M2M field Group model'''
    Group.permissions.db_table = 'group_permissions'
    Group._meta.get_field('permissions').db_table = 'group_permissions'

    '''Edit db_table of Group model'''
    Group._meta.db_table = 'groups'
    Group._meta.original_attrs['db_table'] = 'groups'

    '''Edit db_table of Permission model'''
    Permission._meta.db_table = 'permissions'
    Permission._meta.original_attrs['db_table'] = 'permissions'

    '''Edit db_table of LogEntry model'''
    LogEntry._meta.db_table = 'admin_logs'
    LogEntry._meta.original_attrs['db_table'] = 'admin_logs'

    '''Edit db_table of Session model'''
    Session._meta.db_table = 'sessions'
    Session._meta.original_attrs['db_table'] = 'sessions'

    '''Edit db_table of ContentType model'''
    ContentType._meta.db_table = 'content_types'
    ContentType._meta.original_attrs['db_table'] = 'content_types'

    '''Edit db_table of Migration model'''
    MigrationRecorder._migration_class._meta.db_table = 'migrations'
    MigrationRecorder._migration_class._meta.original_attrs['db_table'] = 'migrations'
