from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, ListField, ValidationError
from datetime import datetime

class Clothes(Document):
    name = StringField(max_length=200, required=True)
    brand = StringField(max_length=100, required=True)
    category = StringField(max_length=50, required=True)
    description = StringField(required=False)
    price = DecimalField(precision=2, required=True)
    sizes = ListField(StringField(max_length=10))
    colors = ListField(StringField(max_length=50))
    material = StringField(max_length=100, required=False)
    gender = StringField(max_length=20, required=True)
    stock = IntField(min_value=0, default=0)
    sku = StringField(max_length=50, required=True, unique=True)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    meta = {
        'db_alias': 'clothes',
        'collection': 'clothes',
        'indexes': ['sku'],
        'ordering': ['-created_at']
    }

    def clean(self):
        # Validation similar to the serializer
        valid_genders = ['Men', 'Women', 'Unisex']
        if self.gender not in valid_genders:
            raise ValidationError(f"Gender must be one of {valid_genders}")

        valid_categories = [
            'Shirt', 'T-Shirt', 'Pants', 'Jeans', 'Dress',
            'Skirt', 'Jacket', 'Coat', 'Sweater', 'Hoodie',
            'Underwear', 'Socks', 'Swimwear', 'Activewear'
        ]
        if self.category not in valid_categories:
            raise ValidationError(f"Category must be one of {valid_categories}")

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(Clothes, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.brand}"