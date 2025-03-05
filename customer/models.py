from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import gettext_lazy as _

class CustomerManager(BaseUserManager):
    def create_user(self, email, user_type, password=None, **extra_fields):
        """
        Tạo và lưu một User với email và password.
        """
        if not email:
            raise ValueError("Email phải được cung cấp!")
        if user_type not in [Customer.UserType.GUEST, Customer.UserType.REGISTERED, Customer.UserType.PREMIUM]:
            raise ValueError("user_type không hợp lệ cho user thường!")

        email = self.normalize_email(email)
        user = self.model(email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Tạo và lưu một superuser với email và password.
        Superuser sẽ có user_type là Admin.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user_type = Customer.UserType.ADMIN

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser phải có is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_superuser=True.')

        email = self.normalize_email(email)
        user = self.model(email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Customer(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        GUEST = 'GUEST', 'Guest'
        REGISTERED = 'REGISTERED', 'Registered'
        PREMIUM = 'PREMIUM', 'Premium'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.GUEST,
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='customer_set',
        help_text=_('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customer_set',
        help_text=_('Specific permissions for this user.'),
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Dành cho admin site

    # Các trường bổ sung khác nếu cần, ví dụ: phone, address,...
    address = models.CharField(max_length=255, blank=True)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email được coi là bắt buộc, còn lại có thể mở rộng

    def __str__(self):
        return self.email

class Address(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_line1 = models.CharField(max_length=255, help_text="Số nhà, tên đường")
    address_line2 = models.CharField(max_length=255, blank=True, null=True, help_text="Thông tin bổ sung (nếu có)")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"
