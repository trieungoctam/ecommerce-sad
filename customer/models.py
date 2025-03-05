from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """
    Custom User Model with 4 type:
    1. Guest
    2. Registered
    3. Premium
    4. Admin
    """

    USER_TYPE = (
        ('guest', 'Guest'),
        ('registered', 'Registered'),
        ('premium', 'Premium'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='guest')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    def get_profile_info(self):
        """
        Get user profile info
        """

        return {
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'user_type': self.user_type,
        }

    def upgrade_to_premium(self):
        """
        Upgrade user to premium
        """

        self.user_type = 'premium'
        self.save()

    def downgrade_to_registered(self):
        """
        Downgrade user to registered
        """

        self.user_type = 'registered'
        self.save()

    def promote_to_admin(self):
        """
        Promote user to admin
        """

        self.user_type = 'admin'
        self.save()

    def is_guest(self):
        """
        Check if user is guest
        """

        return self.user_type == 'guest'

    def is_registered(self):
        """
        Check if user is registered
        """

        return self.user_type == 'registered'

    def is_premium(self):
        """
        Check if user is premium
        """

        return self.user_type == 'premium'

    def is_admin(self):
        """
        Check if user is admin
        """

        return self.user_type == 'admin'