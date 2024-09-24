from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.'
    )
    ROLE_CHOICES = [
        ('user', 'User'),
        ('manager', 'Event Manager'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # Ensure unique email
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    available_tickets = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    tickets_booked = models.IntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='Pending')
