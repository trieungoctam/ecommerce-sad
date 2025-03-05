from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, ListField, BooleanField
from datetime import datetime

class Mobile(Document):
    name = StringField(max_length=200, required=True)
    brand = StringField(max_length=100, required=True)
    model_number = StringField(max_length=100, required=True, unique=True)
    description = StringField()
    price = DecimalField(precision=2, required=True)
    stock = IntField(default=0)

    # Technical Specifications
    screen_size = DecimalField(precision=1, required=True)  # in inches
    ram = IntField(required=True)  # in GB
    storage = IntField(required=True)  # in GB
    battery_capacity = IntField(required=True)  # in mAh
    processor = StringField(max_length=100, required=True)
    operating_system = StringField(max_length=50, required=True)
    camera_specs = StringField(max_length=200, required=True)  # e.g., "48MP + 12MP + 5MP"

    # Features
    colors = ListField(StringField(max_length=50))
    network = StringField(max_length=20, required=True)  # 4G, 5G
    dual_sim = BooleanField(default=False)
    fingerprint_sensor = BooleanField(default=True)
    face_unlock = BooleanField(default=True)
    wireless_charging = BooleanField(default=False)
    fast_charging = BooleanField(default=True)
    water_resistant = BooleanField(default=False)

    # Additional Information
    warranty = IntField(default=12)  # in months
    release_date = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'db_alias': 'mobile',
        'collection': 'mobiles',
        'indexes': [
            'model_number',
            ('brand', 'name'),
            ('price', 'ram', 'storage')
        ],
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Mobile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.model_number})"
