from django.contrib.auth.models import User
from ninja import ModelSchema
from ninja import Schema,Field
from main.models import UserProfile


class UserSchemaIn(ModelSchema):
    class Meta:
        model = User
        fields = ["username","password","first_name","last_name","email","is_active","date_joined"]
class UserSchemaOut(ModelSchema):
    class Meta:
        model = User
        fields = ["id","username"]

class LoginSchema(Schema):
    username:str
    password:str

class UserProfileSchemaIn(ModelSchema):
    class Meta:
        model = UserProfile
        fields = ["profile_pic", "role", "address", "phone_number"]

class UserProfileSchemaOut(ModelSchema):
    class Meta:
        model = UserProfile
        fields = ["id", "user", "profile_pic", "role", "address", "phone_number"]