from rest_framework import serializers
from .models import CustomURL


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomURL
        fields = ['short_url', 'long_url', 'created_at', 'validity_period', 'created_by', 'is_active',
                  'one_time_only', 'password', 'is_deleted']
