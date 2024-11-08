from .services import UserModelService
from .schema import *
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth.models import User
from typing import List, Optional
from ninja_extra import (
    ModelConfig,
    ModelControllerBase,
    ModelSchemaConfig,
    api_controller,
    NinjaExtraAPI,
    permissions,
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
from django.db.models import Q
from django.middleware.csrf import get_token

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

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, controller):
        # Allow access only if the user id is same as obj user id
        user_id = request.path.split('/')
        for i in user_id:
            if(i.isnumeric()):
                return request.auth.id == int(i)
        return False
    # def has_object_permission(self, request, controller, obj):
    #     # Allow access only if the authenticated user is the owner of the object
    #     return request.auth.id == obj.user.id

#First create user with basic details
#Password updation and other critical operations are performed on user model
@api.get("/set-csrf-token")
def get_csrf_token(request):
    return {"csrftoken": get_token(request)}


@api.post('/user/login', tags=['Login'], url_name='login')
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user:
        try:
            profile = UserProfile.objects.get(user=user)
            role = "Admin" if user.is_superuser else profile.role
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'id': profile.user.id,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': role
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile does not exist'}, status=400)
    return JsonResponse({'error': 'Invalid credentials'}, status=400)



@api.post('user/register',tags=['Register'],url_name='register',response=UserSchemaOut)
def Register(request, data:UserSchemaIn):
    user=User.objects.create_user(username=data.username,password=data.password,first_name=data.first_name
                                  ,last_name=data.last_name, email=data.email)
    profile=UserProfile.objects.create(user=user)
    user.save()
    profile.save()
    return user

@api_controller("/user",tags=["UserOperations"],auth=JWTAuth())
class UserModelController(ModelControllerBase):
    service=UserModelService(model=User)
    model_config = ModelConfig(
        model = User,
        allowed_routes=["patch", "delete"],
        schema_config=ModelSchemaConfig(include=["id","password","username","first_name","last_name","email","is_active","date_joined"],
                                        write_only_fields=["id","password"]),
    )
api.register_controllers(UserModelController)

#Hold extra information related to user to setup its profile
@api_controller('/profile', tags=['UserOperations'],auth=JWTAuth(),permissions=[IsOwner])
class ProfileModelController:

    @http_get('/{user_id}', response=UserProfileSchemaOut, url_name='get_user')
    def Get_user(self, request, user_id: int):
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
    @http_patch('/{user_id}', response=UserProfileSchemaOut)
    def patch_profile(self, request, user_id: int, data: UserProfileSchemaIn = None, pic: File[UploadedFile] = None):
        """Partially update a user profile by user ID"""
        profile = UserProfile.objects.get(user__id=user_id)
        fields=UserProfileSchemaIn.Meta.fields
        try:
            if data:
                for attr, value in data.dict().items():

                    if attr in fields:
                        if value is not None:
                            setattr(profile, attr, value)
                    else:

                        return JsonResponse({'error': f'Invalid field: {str(e)}'}, status=400)
            if pic:
                profile.profile_pic.save(pic.name, pic)
            
            profile.save()
            return profile  
        except Exception as e:
            return JsonResponse({'error': f'Error during update: {str(e)}'}, status=500)

api.register_controllers(ProfileModelController)

#Client based operations
@api_controller('/client', tags=['ClientOperations'],auth=JWTAuth(),permissions=[IsOwner])
class ClientModelController:

    @http_get('/{user_id}', response=dict)
    def get_total_points(self, request, user_id: int):
        """Retrieve total points of a user and plastic collected(in kg)"""
        profile = UserProfile.objects.get(user__id=user_id)
        return {'total_points': profile.earned_points,'plastic_collected': profile.total_plastic_recycled}

    @http_get('/{user_id}/badges', response=list)
    def get_badges(self, request, user_id: int):
        """Retrieve badges earned by a user"""
        badges = Badge.objects.filter(user__user__id=user_id)
        return [{'name': badge.name, 'issued_date': badge.issued_date} for badge in badges]
    
    @http_post('/{user_id}/collection', response=dict)
    def post_collection_request(self, user_id: int, amount_collected: float, pic: UploadedFile):
        """Post a request for plastic collection with an image of plastic waste"""
        profile = UserProfile.objects.get(user__id=user_id)
        if not profile.city or not profile.state:
            return JsonResponse({'error': 'Please update your profile details, especially your location'}, status=400)
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
        unclaimed_requests = PlasticCollection.objects.filter(user__user__id=user_id, status='Request')
        pending_requests = PlasticCollection.objects.filter(user__user__id=user_id, status='Pending')
        completed_requests = PlasticCollection.objects.filter(user__user__id=user_id, status='Collected')
        return {
            'unclaimed_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in unclaimed_requests],
            'pending_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in pending_requests],
            'completed_requests': [{'amount_collected': req.amount_collected, 'collection_date': req.collection_date} for req in completed_requests]
        }
    @http_get('/{user_id}/rewards', response=list)
    def list_claimable_rewards(self, user_id: int):
        """List all claimable rewards for a user"""
        profile = UserProfile.objects.get(user__id=user_id)
        claimed_rewards = Reward.objects.filter(user__user__id=user_id).values_list('reward__id', flat=True)
        claimable_rewards = ListReward.objects.exclude(pk__in=claimed_rewards).filter(points_required__lte=profile.earned_points)
        return [{'id': reward.id, 'name': reward.title, 'points_required': reward.points_required} for reward in claimable_rewards]

    @http_post('/{user_id}/rewards/{reward_id}/claim', response=dict)
    def claim_reward(self, request, user_id: int, reward_id: int):
        """Claim a reward for a user"""
        profile = UserProfile.objects.get(user__id=user_id)
        reward = ListReward.objects.get(id=reward_id)
        
        if profile.earned_points >= reward.points_required:
            obj,created = Reward.objects.get_or_create(user=profile, reward=reward)
            if created:
                return {'message': 'Reward claimed successfully'}
            else:
                return JsonResponse({'error': 'Already Claimed.'}, status=400)
            
        return JsonResponse({'error': 'Not enough points to claim this reward'}, status=400)

    @http_get('/{user_id}/rewards/history', response=list)
    def claimed_rewards_history(self, request, user_id: int):
        """Retrieve claimed rewards history of a user"""
        claimed_rewards = Reward.objects.filter(user__user__id=user_id)
        return [{'title': reward.reward.title, 'claimed_date': reward.claimed_date} for reward in claimed_rewards]

api.register_controllers(ClientModelController)

@api_controller('/notifications', tags=['Notifications'],auth=JWTAuth())
class NotificationModelController:

    @http_post('/{user_id}/send', response=dict)
    def send_notification(self, request, user_id: int, message: str, importance_level: Optional[str] = 'Low'):
        """Send a notification to a user"""
        notification = Notification.objects.create(
            user=user_id,
            message=message,
            importance_level=importance_level
        )
        notification.save()
        return {'message': 'Notification sent successfully'}

    @http_get('/{user_id}', response=list)
    def get_notifications(self, request, user_id: int):
        """Retrieve all notifications for a user"""
        notifications = Notification.objects.filter(to_user__user__id=user_id).order_by('-notification_date')
        return [{ 'id': notification.id,'message': notification.message, 'notification_date': notification.notification_date, 'is_read': notification.is_read} for notification in notifications]

    @http_patch('/{notification_id}/read', response=dict)
    def mark_as_read(self, request, notification_id: int):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return {'message': 'Notification does not exist'}
        notification.is_read = True
        notification.save()
        return {'message': 'Notification marked as read'}
    @http_patch('/{user_id}/read/all', response=dict)
    def mark_all_read(self, request, user_id: int):
        """Mark a notification as read"""
        notifications = Notification.objects.filter(to_user__user__id=user_id,is_read=False).order_by('-notification_date')
        if notifications.exists():
            notifications.update(is_read=True)
            return {'message': 'All Notifications marked as read'}
        
        return {'message': 'Already marked as read'}

api.register_controllers(NotificationModelController)


@api_controller('/agent', tags=['AgentOperations'],auth=JWTAuth())
class AgentModelController:

    @http_get('/{user_id}/requests', response={ 200:List[ListCollection], 406:ErrorSchema})
    def list_requests(self, user_id: int):
        """List all unclaimed collection requests, optionally filtered by city or state with fuzzy search"""
        agent_profile = UserProfile.objects.get(user__id=user_id)
        city = agent_profile.city
        state = agent_profile.state
        
        filters = Q(status='Request')
        if city and state:
            filters &= Q(user__city__icontains=city)
            filters &= Q(user__state__icontains=state)
            res = PlasticCollection.objects.filter(filters).order_by('user__city', 'user__state')
            return 200,res
        else:
            return 406,{'message': 'Please update your profile details, especially your location'}
        

    @http_post('/{user_id}/claim', response=dict)
    def claim_collection_request(self, request, user_id: int, collection_id: int):
        """Agent claims a plastic collection request"""
        collection = PlasticCollection.objects.get(id=collection_id, status='Request')
        collection.status = 'Pending'
        collection.agent = UserProfile.objects.get(user__id=user_id)
        collection.save()
        return {'message': 'Collection request claimed successfully'}

    @http_patch('/{user_id}/collect', response=dict)
    def collect_plastic(self, request, user_id: int, collection_id: int):
        """Agent updates the status of a collection request to collected"""
        collection = PlasticCollection.objects.get(id=collection_id, agent__user__id=user_id, status='Pending')
        collection.status = 'Collected'
        collection.save()
        return {'message': 'Plastic collected successfully'}

    @http_get('/{user_id}/history', response=dict)
    def get_agent_requests(self, request, user_id: int):
        """Retrieve pending and completed requests claimed by the agent"""
        pending_requests = PlasticCollection.objects.filter(agent__user__id=user_id, status='Pending')
        completed_requests = PlasticCollection.objects.filter(agent__user__id=user_id, status='Collected')
        return {
            'pending_requests': [{'id': req.id, 
                                  'amount_collected': req.amount_collected, 
                                  'collection_date': req.collection_date} for req in pending_requests],
            'completed_requests': [{'id': req.id, 
                                    'amount_collected': req.amount_collected,
                                    'collection_date': req.collection_date} for req in completed_requests]
        }

api.register_controllers(AgentModelController)
