from rest_framework import serializers
from .models import UserMetaData
import re

class UserMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMetaData
        fields = ['id', 'user', 'email']
        read_only_fields = ['user']

    def validate_email(self, value):
        if not re.match(r'^[A-Za-z0-9._%+-]+@gmail\.com$', value):
            raise serializers.ValidationError("Email must be a valid Gmail address and contain only allowed characters.")

        qs = UserMetaData.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This email is already in use.")

        return value
