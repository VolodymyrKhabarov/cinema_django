"""
This module defines serializer for the User model in the users app.

The UserSerializer class provides serialization and deserialization of User model instances,
converting complex data types to and from JSON format. It also performs validation on the data
during serialization and deserialization.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import User

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer provides serialization and deserialization of User model instances,
converting complex data types to and from JSON format. It also performs validation on the data
during serialization and deserialization.

Attributes:
    ticket_set (HyperlinkedRelatedField): A hyperlinked related field that represents the related
        Ticket objects for the User. This field is read-only.
    password (CharField): A character field that represents the password for the User. This field
        is write-only.
    password_confirmation (CharField): A character field that represents the password confirmation
        for the User. This field is write-only.

Meta:
    model (User): The User model that this serializer serializes.
    fields (tuple): A tuple of strings representing the fields to be serialized and deserialized.
"""

    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirmation', 'is_staff')

    def validate(self, data):
        """
        Verify that the password and password_confirmation fields match.
        """
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError("Email is required")
        user = User.objects.create_user(username=validated_data['username'], email=email,
            password=validated_data['password'])
        return user
