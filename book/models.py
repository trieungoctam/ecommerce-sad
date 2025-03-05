from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, DateField
from datetime import datetime

# Create your models here.

class Book(Document):
    title = StringField(max_length=200, required=True)
    author = StringField(max_length=200, required=True)
    description = StringField()
    price = DecimalField(precision=2, required=True)
    stock = IntField(default=0)
    isbn = StringField(max_length=13, unique=True, required=True)
    published_date = DateField(required=True)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    meta = {
        'db_alias': 'books',
        'collection': 'books',
        'indexes': ['isbn'],
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'books'
        verbose_name_plural = 'books'