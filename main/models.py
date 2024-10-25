from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=[('Client', 'Client'), ('Agent', 'Agent')],default='Client')
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    total_plastic_recycled = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earned_incentives = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username

class PlasticCollection(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount_collected = models.DecimalField(max_digits=6, decimal_places=2)
    collection_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Collected', 'Collected')], default='Pending')

    def __str__(self):
        return f"{self.user.user.username} - {self.amount_collected} kg"

    def save(self, *args, **kwargs):
        if self.status == 'Collected':
            self.user.total_plastic_recycled += self.amount_collected
            self.user.save()
        super().save(*args, **kwargs)

class Incentive(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    incentive_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateTimeField(default=timezone.now)
    reward_type = models.CharField(max_length=100, choices=[('Gift Coupon', 'Gift Coupon'), ('Cash', 'Cash'), ('Offer', 'Offer')])
    threshold_reached = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.user.user.username} - {self.reward_type} - {self.incentive_amount}"

    def save(self, *args, **kwargs):
        if self.user.total_plastic_recycled >= self.threshold_reached:
            self.user.earned_incentives += self.incentive_amount
            self.user.save()
        super().save(*args, **kwargs)
