from .services import UserModelService
from .schema import *
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth.models import User
from ninja_extra import (
    ModelConfig,
    ModelControllerBase,
    ModelSchemaConfig,
    api_controller,
    NinjaExtraAPI,
    
)
from main.models import UserProfile
from ninja import Swagger
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
@api_controller("/profile", tags=["Profile"], auth=JWTAuth())
class ProfileModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=UserProfile,
        allowed_routes=['create', "find_one", "update", "patch", "delete"],
        schema_config=ModelSchemaConfig(read_only_fields=["id"]),
    )
    def get_object_or_none(self, request, *args, **kwargs):
        user_id = kwargs.get('user__id')
        print(**kwargs)
        if user_id:
            return self.model.objects.filter(user__id=user_id).first()
        return super().get_object(request, *args, **kwargs)

api.register_controllers(ProfileModelController)


