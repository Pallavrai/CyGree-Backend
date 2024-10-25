from django.contrib.auth.models import User
from ninja import ModelSchema
from ninja import Schema


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