from django.contrib.auth.models import User
from ninja import ModelSchema
from ninja import Schema,Field
from main.models import UserProfile
from typing import Optional


class UserSchemaIn(ModelSchema):
    class Meta:
        model = User
        fields = ["username","password","first_name","last_name","email","is_active","date_joined"]
class UserSchemaOut(ModelSchema):
    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email","is_active","date_joined"]

class LoginSchema(Schema):
    username:str
    password:str

class UserProfileSchemaIn(ModelSchema):
    class Meta:
        model = UserProfile
        fields = ["profile_pic", "role", "address", "phone_number", "state", "city", "country"]

class UserProfileSchemaOut(ModelSchema):
    user: UserSchemaOut
    profile_pic: Optional[str] = None
    class Meta:
        model = UserProfile
        fields = ["user", "profile_pic", "role", "address", "phone_number", "state", "city", "country", "total_plastic_recycled", "earned_points"]