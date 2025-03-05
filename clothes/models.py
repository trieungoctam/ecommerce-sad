import datetime
from mongoengine import Document, StringField, DecimalField, BooleanField, DateTimeField

class Clothes(Document):
    name = StringField(required=True, max_length=255)
    brand = StringField(required=True, max_length=100)
    size = StringField(required=True, max_length=10, help_text="Kích cỡ (S, M, L, XL, ...)")
    color = StringField(max_length=50)
    material = StringField(max_length=100, help_text="Chất liệu (cotton, polyester, ...)")
    price = DecimalField(precision=2, rounding="ROUND_HALF_UP", required=True)
    available = BooleanField(default=True)
    description = StringField()
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'db_alias': 'clothes',  # Sử dụng kết nối với alias 'clothes'
        'collection': 'clothes',  # Tên collection trong MongoDB
        'ordering': ['-created']
    }

    def __str__(self):
        return f"{self.brand} {self.name} (Size: {self.size})"
