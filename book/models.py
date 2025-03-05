import datetime
from mongoengine import Document, StringField, DateTimeField, DecimalField, BooleanField

class Book(Document):
    title = StringField(required=True, max_length=255)
    description = StringField()
    author = StringField(required=True, max_length=255)
    publisher = StringField(max_length=255)
    isbn = StringField(required=True, unique=True, max_length=20)
    publication_date = DateTimeField()
    price = DecimalField(precision=2, rounding="ROUND_HALF_UP")
    available = BooleanField(default=True)
    created = DateTimeField(default=datetime.datetime.now())
    updated = DateTimeField(default=datetime.datetime.now())

    meta = {
        'db_alias': 'book',  # Sử dụng kết nối đã định nghĩa ở trên
        'collection': 'books',  # Tên collection trong MongoDB
        'ordering': ['-created']
    }

    def __str__(self):
        return self.title
