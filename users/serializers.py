from django.contrib.auth.models import Permission, Group, update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta


from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        password = validated_data['password']
        validate_password(password)
        user = User.objects.create(username=validated_data['username'], first_name=validated_data['first_name'],
                                   last_name=validated_data['last_name'], email=validated_data['email'])
        user.set_password(password)
        if 'groups' in validated_data:
            user.groups.set(validated_data['groups'])
        user.save()
        return user

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        if 'password' in validated_data:
            password = validated_data['password']
            validate_password(password)
            instance.set_password(password)

        instance.save()

        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
