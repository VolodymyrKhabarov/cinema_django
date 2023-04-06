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
    Serializer class for the User model.

    This serializer is used for retrieving and creating user objects.

    Attributes:
    -----------
    total_sum : ReadOnlyField
        The total sum of money spent by the user.
    password : CharField
        The password of the user. This field is write-only.
    password_confirmation : CharField
        The password confirmation of the user. This field is write-only.
    """

    total_sum = serializers.ReadOnlyField(source='user.total_sum')
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        """
        Metadata for UserSerializer.
        """
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirmation', 'total_sum', 'wallet')
        read_only_fields = ['total_sum', 'wallet']

    def to_representation(self, instance):
        """
        Convert the User model instance to a Python dict.

        This method adds the `total_sum` field to the serialized representation.

        Parameters:
        -----------
        instance : User
            The User model instance.

        Returns:
        --------
        dict
            A Python dict representing the serialized User model instance.
        """
        data = super().to_representation(instance)
        data['total_sum'] = instance.total_sum
        return data

    def validate(self, data):
        """
        Validate the input data.

        This method verifies that the password and password_confirmation fields match.

        Parameters:
        -----------
        data : dict
            A dictionary containing the input data.

        Returns:
        --------
        dict
            The validated input data.
        Raises:
        ------
        serializers.ValidationError
            If the password and password_confirmation fields do not match.
        """
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """
        Create a new user.

        This method creates a new user object using the input data.

        Parameters:
        -----------
        validated_data : dict
            A dictionary containing the validated input data.

        Returns:
        --------
        User
            The newly created user object.
        Raises:
        ------
        serializers.ValidationError
            If the email field is missing.
        """
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError("Email is required")
        user = User.objects.create_user(username=validated_data['username'], email=email,
                                        password=validated_data['password'])
        return user
