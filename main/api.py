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
from main.models import UserProfile
from ninja import Swagger,UploadedFile,File
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage

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
                                  ,last_name=data.last_name, email=data.email)
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

STORAGE = FileSystemStorage()


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
