from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, ListField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime

class SizeConversion(EmbeddedDocument):
    us = DecimalField(precision=1)  # US size
    uk = DecimalField(precision=1)  # UK size
    eu = IntField()                 # EU size
    cm = DecimalField(precision=1)  # Length in centimeters

class Shoes(Document):
    name = StringField(max_length=200, required=True)
    brand = StringField(max_length=100, required=True)
    sku = StringField(max_length=50, required=True, unique=True)
    description = StringField()
    price = DecimalField(precision=2, required=True)
    stock = IntField(default=0)

    # Shoe Specifications
    category = StringField(max_length=50, required=True)  # Sneakers, Boots, Formal, etc.
    gender = StringField(max_length=20, required=True)  # Men, Women, Unisex, Kids
    available_sizes = ListField(EmbeddedDocumentField(SizeConversion))  # List of available sizes with conversions
    colors = ListField(StringField(max_length=50))

    # Material and Construction
    upper_material = StringField(max_length=100)  # Leather, Canvas, Mesh, etc.
    sole_material = StringField(max_length=100)  # Rubber, EVA, etc.
    closure_type = StringField(max_length=50)  # Laces, Velcro, Slip-on
    insole_type = StringField(max_length=100)  # Memory foam, Regular, etc.

    # Features
    is_waterproof = BooleanField(default=False)
    is_orthopedic = BooleanField(default=False)
    is_athletic = BooleanField(default=False)
    has_arch_support = BooleanField(default=False)

    # Style and Usage
    style = StringField(max_length=50)  # Casual, Formal, Sport, etc.
    occasion = StringField(max_length=50)  # Casual, Formal, Athletic, etc.
    season = ListField(StringField(max_length=20))  # [Summer, Winter, etc.]

    # Additional Information
    warranty = IntField(default=0)  # in months
    care_instructions = StringField()
    release_date = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # Size Information
    size_chart = DictField()  # Additional size information and measurements
    fit_type = StringField(max_length=50)  # Regular, Wide, Narrow
    heel_height = DecimalField(precision=1)  # in inches
    weight = DecimalField(precision=2)  # in kg

    # Inventory Management
    size_inventory = DictField()  # Track stock by size
    low_stock_threshold = IntField(default=5)
    is_discontinued = BooleanField(default=False)

    # Additional Features
    sustainability_rating = IntField(min_value=1, max_value=5)  # Eco-friendliness rating
    comfort_rating = IntField(min_value=1, max_value=5)
    durability_rating = IntField(min_value=1, max_value=5)
    return_policy = StringField()
    shipping_weight = DecimalField(precision=2)  # in kg
    box_dimensions = StringField()  # LxWxH in cm

    meta = {
        'db_alias': 'shoes',
        'collection': 'shoes',
        'indexes': [
            'sku',
            ('brand', 'name'),
            ('category', 'gender'),
            ('price', 'category'),
            'fit_type',
            'sustainability_rating'
        ],
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Shoes, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} - {self.name} ({self.category})"

    def get_available_sizes_for_region(self, region='US'):
        """Get available sizes for a specific region."""
        sizes = []
        for size in self.available_sizes:
            if region == 'US':
                sizes.append(size.us)
            elif region == 'UK':
                sizes.append(size.uk)
            elif region == 'EU':
                sizes.append(size.eu)
            else:
                sizes.append(size.cm)
        return sorted(sizes)

    def update_size_inventory(self, size_data):
        """Update inventory for specific sizes."""
        for size, quantity in size_data.items():
            self.size_inventory[str(size)] = quantity
        self.stock = sum(int(qty) for qty in self.size_inventory.values())
        self.save()

    def check_size_availability(self, size, region='US'):
        """Check if a specific size is available."""
        size_key = str(size)
        return self.size_inventory.get(size_key, 0) > 0

    def is_low_stock(self, size=None):
        """Check if shoe or specific size is low in stock."""
        if size:
            size_key = str(size)
            return self.size_inventory.get(size_key, 0) <= self.low_stock_threshold
        return self.stock <= self.low_stock_threshold
