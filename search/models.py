from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)  # Store search filters
    results_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Search histories'

    def __str__(self):
        return f"{self.user.username} - {self.query}"

class PopularSearch(models.Model):
    query = models.CharField(max_length=255, unique=True)
    count = models.IntegerField(default=0)
    last_searched = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'popular_searches'
        ordering = ['-count']

    def __str__(self):
        return f"{self.query} ({self.count} searches)"

    @classmethod
    def increment_search(cls, query):
        obj, created = cls.objects.get_or_create(
            query=query,
            defaults={'count': 1, 'last_searched': timezone.now()}
        )
        if not created:
            obj.count += 1
            obj.last_searched = timezone.now()
            obj.save()
        return obj
