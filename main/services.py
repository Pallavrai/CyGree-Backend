from django.contrib.auth.models import User
from ninja_extra import ModelService
from django.contrib.auth.hashers import make_password

class UserModelService(ModelService):
    def create(self, schema, **kwargs):
        data = schema.model_dump(by_alias=True)
        print(data)
        data['password'] = make_password(data['password'])
        data.update(kwargs)
        instance = self.model._default_manager.create(**data)
        return instance

    def patch(self, instance, schema, **kwargs):
        data = schema.model_dump(exclude_unset=True)
        if 'password' in data:
            data['password'] = make_password(data['password'])
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
