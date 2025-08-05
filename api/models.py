from django.db import models
from authentication.models import CommonModel
from authentication import models as auth_models
import requests
from django.conf import settings
import math
from authentication.models import CustomUser

class Trip(CommonModel):
    user = models.ForeignKey(auth_models.CustomUser, on_delete=models.CASCADE, related_name='trips')
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    image = models.ImageField(upload_to='trip_images/')
    # end_date = models.DateField()
    # currency = models.FloatField()
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        db_table = 'trips'
        verbose_name_plural = 'Trips'

    def __str__(self):
        return self.destination

class Category(CommonModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,related_name='categories')
    category_name = models.CharField(max_length=50, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    color_code = models.CharField(max_length=7,null=True)
    class Meta:
        ordering = ['-created_at']
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category_name'],
                name='unique_category_per_user'
            )
        ]

    def __str__(self):
        return f'{self.category_name}'

    
class Expense(CommonModel):
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('cash', 'Cash'),
    ]
    user = models.ForeignKey(auth_models.CustomUser,on_delete=models.CASCADE, related_name='user_expense')
    trip = models.ForeignKey(Trip, max_length=50, on_delete=models.CASCADE, related_name='user_trip')
    expense = models.DecimalField(max_digits=15,decimal_places=2, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='user_category')
    date = models.DateField()
    remarks = models.TextField(blank=True)
    bill_receipt = models.ImageField(upload_to='bill_receipt/')
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='online')

    class Meta:
        ordering=['-created_at']
        db_table='expenses'
        verbose_name_plural='Expenses'

    def __str__(self):
        return f"{self.expense} - {self.category.category_name} on {self.date}"



    
