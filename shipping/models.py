from django.db import models
from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, BooleanField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
from datetime import datetime

# Create your models here.

class Address(EmbeddedDocument):
    street = StringField(required=True)
    city = StringField(required=True)
    state = StringField(required=True)
    country = StringField(required=True)
    postal_code = StringField(required=True)
    is_default = BooleanField(default=False)
    phone = StringField()
    instructions = StringField()

class ShippingMethod(Document):
    name = StringField(required=True)  # Express, Standard, Economy
    carrier = StringField(required=True)  # FedEx, UPS, DHL
    estimated_days = IntField(required=True)
    tracking_available = BooleanField(default=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'shipping_methods',
        'indexes': ['name', 'carrier']
    }

    def __str__(self):
        return f"{self.carrier} - {self.name} ({self.estimated_days} days)"

class ShippingRate(Document):
    shipping_method = ReferenceField(ShippingMethod, required=True)
    country = StringField(required=True)
    base_rate = DecimalField(precision=2, required=True)
    weight_rate = DecimalField(precision=2, required=True)  # Additional cost per kg
    min_weight = DecimalField(precision=2, default=0.0)
    max_weight = DecimalField(precision=2)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'shipping_rates',
        'indexes': [
            ('shipping_method', 'country'),
            ('country', 'is_active')
        ]
    }

    def calculate_shipping_cost(self, weight):
        if weight < self.min_weight or weight > self.max_weight:
            raise ValueError("Weight is outside acceptable range")
        return self.base_rate + (weight * self.weight_rate)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
