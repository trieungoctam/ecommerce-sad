class DatabaseRouter:
    """
    A router to control all database operations on models for different databases.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to default db.
        """
        from django.conf import settings
        if hasattr(model, '_meta'):
            app_label = model._meta.app_label
            if app_label in settings.DATABASE_APPS_MAPPING:
                return settings.DATABASE_APPS_MAPPING[app_label]
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to default db.
        """
        from django.conf import settings
        if hasattr(model, '_meta'):
            app_label = model._meta.app_label
            if app_label in settings.DATABASE_APPS_MAPPING:
                return settings.DATABASE_APPS_MAPPING[app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is involved.
        """
        from django.conf import settings
        db1 = settings.DATABASE_APPS_MAPPING.get(obj1._meta.app_label)
        db2 = settings.DATABASE_APPS_MAPPING.get(obj2._meta.app_label)
        if db1 and db2:
            return db1 == db2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the default database.
        """
        from django.conf import settings
        if app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[app_label] == db
        return None