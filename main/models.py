from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic=models.ImageField(upload_to='profile_pics/',default='profile_pics/default.jpg')
    role = models.CharField(max_length=100, choices=[('Client', 'Client'), ('Agent', 'Agent')],default='Client')
    address = models.CharField(max_length=255, blank=True, null=True)
    
    CITY_CHOICES = {
        'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore'],
        'Arunachal Pradesh': ['Itanagar', 'Naharlagun'],
        'Assam': ['Guwahati', 'Silchar', 'Dibrugarh'],
        'Bihar': ['Patna', 'Gaya', 'Bhagalpur'],
        'Chhattisgarh': ['Raipur', 'Bhilai', 'Bilaspur'],
        'Goa': ['Panaji', 'Margao'],
        'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
        'Haryana': ['Gurgaon', 'Faridabad', 'Panipat'],
        'Himachal Pradesh': ['Shimla', 'Dharamshala'],
        'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad'],
        'Karnataka': ['Bengaluru', 'Mysuru', 'Mangaluru'],
        'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode'],
        'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior'],
        'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik'],
        'Manipur': ['Imphal'],
        'Meghalaya': ['Shillong'],
        'Mizoram': ['Aizawl'],
        'Nagaland': ['Kohima', 'Dimapur'],
        'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela'],
        'Punjab': ['Chandigarh', 'Ludhiana', 'Amritsar'],
        'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur'],
        'Sikkim': ['Gangtok'],
        'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai'],
        'Telangana': ['Hyderabad', 'Warangal'],
        'Tripura': ['Agartala'],
        'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi'],
        'Uttarakhand': ['Dehradun', 'Haridwar'],
        'West Bengal': ['Kolkata', 'Howrah', 'Durgapur'],
        'Andaman and Nicobar Islands': ['Port Blair'],
        'Chandigarh': ['Chandigarh'],
        'Dadra and Nagar Haveli and Daman and Diu': ['Daman', 'Silvassa'],
        'Lakshadweep': ['Kavaratti'],
        'Delhi': ['New Delhi'],
        'Puducherry': ['Puducherry'],
        'Ladakh': ['Leh'],
        'Jammu and Kashmir': ['Srinagar', 'Jammu'],
    }

    city = models.CharField(max_length=255, blank=True, null=True, choices=[(city, city) for state in CITY_CHOICES.values() for city in state])
    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Delhi', 'Delhi'),
        ('Puducherry', 'Puducherry'),
        ('Ladakh', 'Ladakh'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ]
    state = models.CharField(max_length=255, choices=STATE_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=255, default="India")
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    total_plastic_recycled = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    earned_points = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username
    
''' 
User will request for plastic collection with its picture and amount then
agent will claim the request and collect the plastic during this phase status will be pending
after collecting the plastic agent will update the status to collected
and we will initiate reward for user based on the amount of plastic collected
'''
class PlasticCollection(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent=models.ForeignKey(UserProfile, on_delete=models.SET_NULL, related_name='agent',null=True,blank=True)
    collection_pic=models.ImageField(upload_to='plastic_collection/',default='default.jpg')
    amount_collected = models.DecimalField(max_digits=6, decimal_places=2)
    collection_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[('Request', 'Request'),('Pending', 'Pending'), ('Collected', 'Collected')], default='Request')

    def __str__(self):
        return f"{self.user.user.username} - {self.amount_collected} kg"

    def save(self, *args, **kwargs):
        if self.status == 'Collected':
            self.user.total_plastic_recycled += self.amount_collected
            self.user.earned_points += self.amount_collected * 10
            self.user.save()
        super().save(*args, **kwargs)

class ListReward(models.Model):
    title = models.CharField(max_length=100,null=True)
    points_required = models.DecimalField(max_digits=30,decimal_places=2)
    issued_date = models.DateTimeField(default=timezone.now)
    reward_type = models.CharField(max_length=100, choices=[('Gift Coupon', 'Gift Coupon'), ('Cash', 'Cash'), ('Offer', 'Offer')])

    def __str__(self):
        return f"{self.reward_type} - {self.points_required}"

    # def save(self, *args, **kwargs):
    #     if self.user.total_plastic_recycled >= self.threshold_reached:
    #         self.user.earned_points += self.listreward_amount
    #         self.user.save()
    #     super().save(*args, **kwargs)
class Reward(models.Model):
        user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
        reward = models.ForeignKey(ListReward, on_delete=models.CASCADE)
        claimed_date = models.DateTimeField(default=timezone.now)

        def __str__(self):
            return f"{self.user.user.username} - {self.reward.reward_type}"

        def save(self, *args, **kwargs):
            if self.user.earned_points >= self.reward.points_required:
                self.user.earned_points -= self.reward.points_required
                self.user.save()
            else:
                raise ValidationError(
                    ('Not enough points to claim this reward'))
            super().save(*args, **kwargs)
        class Meta:
            unique_together = ["user", "reward"]

class Badge(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    BADGES = [
        ('Recycler', 'Recycler'),
        ('Eco Warrior', 'Eco Warrior'),
        ('Green Ambassador', 'Green Ambassador'),
        ('Sustainability Hero', 'Sustainability Hero'),
    ]

    name = models.CharField(
        max_length=100,
        choices=BADGES,
        default='Recycler',
    )
    issued_date = models.DateTimeField(default=timezone.now)

class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='to_user', null=True, blank=True)
    message = models.TextField()
    importance_level = models.CharField(max_length=50, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low')
    notification_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-importance_level', '-notification_date']

    def __str__(self):
        return f"{self.user.user.username} - {self.importance_level} - {self.message[:20]}"

    def save(self, *args, **kwargs):
        if 'role change' in self.message.lower():
            self.importance_level = 'High'
        elif 'badge' in self.message.lower():
            self.importance_level = 'Medium'
        super().save(*args, **kwargs)