from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.models import User

from diap.models.callback import CallBack
from diap.models.front import ImportantNews
from diap.models.person import Person, PersonImage, PersonText, PersonPlaceWhereHeWas, PersonSocialNetwork
from diap.models.choices import PersonTypeSocialNetworkChoices, StatusPersonPostChoices
from diap.models.telegram import TelegramUser


class SocialNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonTypeSocialNetworkChoices
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class PersonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonImage
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = PersonImage
        fields = ("id", 'image', 'person', 'main_image', 'time_create', 'time_update',)


class PersonTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonText
        fields = '__all__'


class PersonPlaceWhereHeWasSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonPlaceWhereHeWas
        fields = '__all__'


class PersonSocialNetworkSerializer(serializers.ModelSerializer):
    # type = SocialNetworkSerializer(many=True, read_only=True)
    class Meta:
        model = PersonSocialNetwork
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    images = PersonImageSerializer(many=True, required=False)
    texts = PersonTextSerializer(many=True, required=False)
    place_where_he_was = PersonPlaceWhereHeWasSerializer(many=True, required=False)
    social_networks = PersonSocialNetworkSerializer(many=True, required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        images_data = validated_data.pop('images')
        texts_data = validated_data.pop('texts')
        place_where_he_was_data = validated_data.pop('place_where_he_was')
        social_networks_data = validated_data.pop('social_networks')
        person = Person.objects.create(**validated_data)
        for image in images_data:
            PersonImage.objects.create(person=person, **image)
        for text in texts_data:
            PersonText.objects.create(person=person, **text)
        for place_where_he_was in place_where_he_was_data:
            PersonPlaceWhereHeWas.objects.create(person=person, **place_where_he_was)
        for social_networks in social_networks_data:
            PersonSocialNetwork.objects.create(person=person, **social_networks)

        return person


class TelegramUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Неверные учетные данные')

        attrs['user'] = user
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'pk', 'is_active']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            is_active=False
        )
        return user


class CallBackSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CallBack
        fields = ('title', 'text', 'person_id')

    def create(self, validated_data):
        person_id = validated_data.pop('person_id')
        person = get_object_or_404(Person, id=person_id)
        return CallBack.objects.create(
            title=validated_data['title'],
            text=validated_data['text'],
            user=validated_data['user'],
            person=person
        )


class PersonImageMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonImage
        fields = ('image',)


class PersonMessageSerializer(serializers.ModelSerializer):
    images = PersonImageSerializer(many=True)
    post_status = serializers.CharField(default=StatusPersonPostChoices.INCOMING, read_only=True)

    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'images',
            'post_status',
            'citizenship',
            'place_of_birthday',
            'place_of_living',
            'place_where_accident',
            'data_when_accident_day',
            'data_when_accident_month',
            'data_when_accident_year',
            'place_of_rip',
            'place_of_rip_date_day',
            'place_of_rip_date_month',
            'place_of_rip_date_year',
            'type_of_army_choice',
            'rank_choice',
            'job_title',
            'military_unit',
            'military_from',
            'additional_info',
            'source',
        )

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        person = Person.objects.create(post_status=StatusPersonPostChoices.INCOMING, **validated_data)
        for image_data in images_data:
            PersonImage.objects.create(person=person, **image_data)

        return person

