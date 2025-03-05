import datetime
from mongoengine import Document, StringField, IntField, DecimalField, BooleanField, DateTimeField

class Shoe(Document):
    name = StringField(required=True, max_length=255)
    brand = StringField(required=True, max_length=100)
    size = IntField(required=True, help_text="Kích cỡ giày")
    color = StringField(max_length=50)
    price = DecimalField(precision=2, rounding="ROUND_HALF_UP", required=True)
    available = BooleanField(default=True)
    description = StringField()
    created = DateTimeField(default=datetime.datetime.now())
    updated = DateTimeField(default=datetime.datetime.now())

    meta = {
        'db_alias': 'shoes',    # Sử dụng kết nối shoes_db
        'collection': 'shoes',     # Tên collection trong MongoDB
        'ordering': ['-created']
    }

    def __str__(self):
        return f"{self.brand} - {self.name} (Size {self.size})"
