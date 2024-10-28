from .services import UserModelService
from .schema import *
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth.models import User
from typing import Optional
from ninja_extra import (
    ModelConfig,
    ModelControllerBase,
    ModelSchemaConfig,
    api_controller,
    NinjaExtraAPI,
    http_post,  
    http_get,   
    http_put,   
    http_patch, 
    http_delete 
)
from main.models import *
from ninja import Swagger,UploadedFile,File
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from django.http import JsonResponse

api = NinjaExtraAPI(title="CyGree",description="""
  <p>Cygree is designed to transform the way we handle plastic waste. This API enables users to recycle plastics efficiently while earning valuable incentives.</p>
  
  <h3>Key Features:</h3>
  <ul>
    <li><strong>Track Plastic Waste:</strong> Users can log and track their plastic waste contributions effortlessly.</li>
    <li><strong>Earn Incentives:</strong> For each plastic item recycled, users earn points redeemable for discounts, vouchers, or eco-friendly products.</li>
    <li><strong>Real-Time Updates:</strong> Provide users with real-time updates on their recycling progress and incentive balances.</li>
    <li><strong>Eco-Friendly Impact:</strong> Showcase the positive environmental impact of users' recycling efforts.</li>
    <li><strong>Secure and Scalable:</strong> Built with robust security measures and scalable architecture to handle high volumes of data and interactions.</li>
  </ul>
  
  <p>By integrating Cygree, businesses and developers can contribute to a greener planet while engaging users in a rewarding recycling journey. Together, we can reduce plastic waste and create a sustainable future.</p>
""",urls_namespace='api',docs=Swagger({"persistAuthorization": True})
                    )

api.register_controllers(NinjaJWTDefaultController)

#First create user with basic details
#Password updation and other critical operations are performed on user model

@api.post('/user/login',tags=['Login'],url_name='login')
def login(request, data: LoginSchema):
        user = authenticate(username=data.username, password=data.password)
        if user:
            profile = UserProfile.objects.get(user=user)
            role = "Admin" if user.is_superuser else profile.role
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'id': profile.user.id,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': role
            })
        return JsonResponse({'error': 'Invalid credentials'}, status=400)



@api.post('user/register',tags=['Register'],url_name='register',response=UserSchemaOut)
def Register(request, data:UserSchemaIn):
    user=User.objects.create_user(username=data.username,password=data.password,first_name=data.first_name
                                  ,last_name=data.last_name)
    profile=UserProfile.objects.create(user=user)
    user.save()
    profile.save()
    return user

@api_controller("/user",tags=["UserOperations"])
class UserModelController(ModelControllerBase):
    service=UserModelService(model=User)
    model_config = ModelConfig(
        model = User,
        allowed_routes=["update", "delete"],
        schema_config=ModelSchemaConfig(include=["id","password","username","first_name","last_name","email","is_active","date_joined"],
                                        write_only_fields=["id","password"]),
    )
api.register_controllers(UserModelController)

#Hold extra information related to user to setup its profile
@api_controller('/profile', tags=['UserOperations'])
class ProfileModelController:

    @http_get('/{user_id}', response=UserProfileSchemaOut)
    def find_one(self, request, user_id: int):
        """Retrieve a user profile by user ID"""
        profile = UserProfile.objects.get(user__id=user_id)
        return profile

    # @http_put('/{user_id}', response=UserProfileSchemaOut)
    # def update_profile(self, request, user_id: int, data: UserProfileSchemaIn):
    #     """Update a user profile by user ID"""
    #     profile = UserProfile.objects.get(user__id=user_id)
    #     for attr, value in data.dict().items():
    #         setattr(profile, attr, value)
    #     profile.save()
    #     return profile

    @http_post('/{user_id}', response=UserProfileSchemaOut)
    def patch_profile(self, request, user_id: int, data: UserProfileSchemaIn = None, pic:File[UploadedFile]=None):
        """Partially update a user profile by user ID"""
        profile = UserProfile.objects.get(user__id=user_id)
    
        if data:
            for attr, value in data.dict().items():
                if value is not None:
                    setattr(profile, attr, value)
        if pic:
            profile.profile_pic.save(pic.name, pic)
        
        profile.save()
        return profile

api.register_controllers(ProfileModelController)

#Client based operations
@api_controller('/client', tags=['ClientOperations'])
class ClientModelController:

    @http_get('/{user_id}', response=dict)
    def get_total_points(self, request, user_id: int):
        """Retrieve total points of a user and plastic collected(in kg)"""
        profile = UserProfile.objects.get(user__id=user_id)
        return {'total_points': profile.earned_points,'plastic_collected': profile.total_plastic_recycled}

    @http_get('/{user_id}/badges', response=list)
    def get_badges(self, request, user_id: int):
        """Retrieve badges earned by a user"""
        badges = Badge.objects.filter(user__id=user_id)
        return [{'name': badge.name, 'issued_date': badge.issued_date} for badge in badges]
    
    @http_post('/{user_id}/collection', response=dict)
    def post_collection_request(self, request, user_id: int, amount_collected: float, pic: UploadedFile):
        """Post a request for plastic collection with an image of plastic waste"""
        profile = UserProfile.objects.get(user__id=user_id)
        collection = PlasticCollection.objects.create(
            user=profile,
            amount_collected=amount_collected,
            collection_pic=pic,
            status='Request'
        )
        collection.collection_pic.save(pic.name, pic)
        collection.save()
        return {'message': 'Collection request posted successfully'}
    @http_get('/{user_id}/history', response=dict)
    def get_history(self, request, user_id: int):
        """Retrieve history of plastic collections showing pending and completed requests"""
        unclaimed_requests = PlasticCollection.objects.filter(user__id=user_id, status='Request')
        pending_requests = PlasticCollection.objects.filter(user__id=user_id, status='Pending')
        completed_requests = PlasticCollection.objects.filter(user__id=user_id, status='Collected')
        return {
            'unclaimed_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in unclaimed_requests],
            'pending_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in pending_requests],
            'completed_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in completed_requests]
        }
    @http_get('/{user_id}/rewards', response=list)
    def list_claimable_rewards(self, request, user_id: int):
        """List all claimable rewards for a user"""
        profile = UserProfile.objects.get(user__id=user_id)
        claimed_rewards = Reward.objects.filter(user__id=user_id).values_list('reward__id', flat=True)
        claimable_rewards = ListReward.objects.exclude(id__in=claimed_rewards).filter(points_required__lte=profile.earned_points)
        return [{'id': reward.id, 'name': reward.title, 'points_required': reward.points_required} for reward in claimable_rewards]

    @http_post('/{user_id}/rewards/{reward_id}/claim', response=dict)
    def claim_reward(self, request, user_id: int, reward_id: int):
        """Claim a reward for a user"""
        profile = UserProfile.objects.get(user__id=user_id)
        reward = ListReward.objects.get(id=reward_id)
        
        if profile.earned_points >= reward.points_required:
            Reward.objects.create(user=profile, reward=reward)
            profile.save()
            return {'message': 'Reward claimed successfully'}
        return JsonResponse({'error': 'Not enough points to claim this reward'}, status=400)

    @http_get('/{user_id}/rewards/history', response=list)
    def claimed_rewards_history(self, request, user_id: int):
        """Retrieve claimed rewards history of a user"""
        claimed_rewards = Reward.objects.filter(user__id=user_id)
        return [{'name': reward.reward.title, 'claimed_date': reward.claimed_date} for reward in claimed_rewards]

api.register_controllers(ClientModelController)

@api_controller('/notifications', tags=['Notifications'])
class NotificationModelController:

    @http_post('/send', response=dict)
    def send_notification(self, request, user_id: int, message: str, importance_level: Optional[str] = 'Low'):
        """Send a notification to a user"""
        profile = UserProfile.objects.get(user__id=user_id)
        notification = Notification.objects.create(
            user=profile,
            message=message,
            importance_level=importance_level
        )
        notification.save()
        return {'message': 'Notification sent successfully'}

    @http_get('/{user_id}', response=list)
    def get_notifications(self, request, user_id: int):
        """Retrieve all notifications for a user"""
        notifications = Notification.objects.filter(to_user__id=user_id).order_by('-notification_date')
        return [{ 'id': notification.id,'message': notification.message, 'notification_date': notification.notification_date, 'is_read': notification.is_read} for notification in notifications]

    @http_patch('/{notification_id}/read', response=dict)
    def mark_as_read(self, request, notification_id: int):
        """Mark a notification as read"""
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return {'message': 'Notification marked as read'}

api.register_controllers(NotificationModelController)

