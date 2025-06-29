from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Location, TextSnippet, AudioSnippet, Tour


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'raw_text', 'version', 'latlon_json', 'created', 'updated']
        read_only_fields = ['created', 'updated']

    def update(self, instance, validated_data):
        # Increment version on content changes
        if 'raw_text' in validated_data and validated_data['raw_text'] != instance.raw_text:
            validated_data['version'] = instance.version + 1
        return super().update(instance, validated_data)


class TextSnippetSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = TextSnippet
        fields = ['id', 'location', 'location_name', 'length', 'text', 'hash', 'is_current', 'created', 'updated']
        read_only_fields = ['created', 'updated', 'hash']


class AudioSnippetSerializer(serializers.ModelSerializer):
    text_snippet_info = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioSnippet
        fields = ['id', 'text_snippet', 'text_snippet_info', 'voice_id', 'audio_url', 'is_current', 'created']
        read_only_fields = ['created']
    
    def get_text_snippet_info(self, obj):
        return {
            'location_name': obj.text_snippet.location.name,
            'length': obj.text_snippet.length
        }


class TourSerializer(serializers.ModelSerializer):
    location_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tour
        fields = ['id', 'name', 'description', 'location_order_json', 'location_count', 'created', 'updated']
        read_only_fields = ['created', 'updated']
    
    def get_location_count(self, obj):
        return len(obj.location_order_json) if obj.location_order_json else 0


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')
