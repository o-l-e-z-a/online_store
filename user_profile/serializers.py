from djoser.serializers import UserCreateSerializer


class RegistrationSerializer(UserCreateSerializer):
    """ Сериализатор для регистрации """

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'telephone', 'first_name', 'last_name', 'date_birthday', 'password')