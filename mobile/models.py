import datetime
from mongoengine import Document, StringField, DateTimeField, IntField, DecimalField, BooleanField

class Mobile(Document):
    brand = StringField(required=True, max_length=100)
    model_name = StringField(required=True, max_length=100)
    operating_system = StringField(max_length=50)
    storage_capacity = IntField(required=True, help_text="Dung lượng lưu trữ (GB)")
    ram = IntField(required=True, help_text="Dung lượng RAM (GB)")
    price = DecimalField(precision=2, rounding="ROUND_HALF_UP", required=True)
    available = BooleanField(default=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'db_alias': 'mobile',   # Dùng kết nối đã định nghĩa ở trên
        'collection': 'mobiles',     # Tên collection trong mobile_db
        'ordering': ['-created']
    }

    def __str__(self):
        return f"{self.brand} {self.model_name}"
