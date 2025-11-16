"""
Serializers para el app base
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    OpcionGeneral, Auditoria, Lugar, Servicio,
    Adicional, Cliente, Chofer, Guia, Horario, Responsable,
    ServicioPrecioEspecial, ServicioParada
)


class OpcionGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionGeneral
        fields = '__all__'


class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(
        source='usuario.username', read_only=True)
    accion_display = serializers.CharField(
        source='get_accion_display', read_only=True)
    modelo = serializers.SerializerMethodField()

    class Meta:
        model = Auditoria
        fields = '__all__'

    def get_modelo(self, obj):
        return str(obj.content_type)


class LugarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lugar
        fields = '__all__'


class ServicioParadaSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)

    class Meta:
        model = ServicioParada
        fields = '__all__'


class ServicioPrecioEspecialSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)
    cliente_nombre = serializers.CharField(
        source='cliente.nombre', read_only=True)

    class Meta:
        model = ServicioPrecioEspecial
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    paradas = ServicioParadaSerializer(many=True, read_only=True)
    precios_especiales_activos = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = '__all__'

    def get_precios_especiales_activos(self, obj):
        """Devuelve solo los precios especiales activos"""
        precios = obj.precios_especiales.filter(activo=True)
        return ServicioPrecioEspecialSerializer(precios, many=True).data


class AdicionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adicional
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class HorarioSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)
    lugar_nombre = serializers.CharField(source='lugar.nombre', read_only=True)

    class Meta:
        model = Horario
        fields = '__all__'


class GuiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        fields = '__all__'


class ChoferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chofer
        fields = '__all__'


class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    grupos = serializers.SerializerMethodField()
    groups = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=User.groups.field.remote_field.model.objects.all()
    )
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_active', 'is_staff', 'grupos', 'groups', 'password']

    def get_grupos(self, obj):
        return [{'id': grupo.id, 'name': grupo.name} for grupo in obj.groups.all()]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', [])
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        if groups:
            user.groups.set(groups)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        if groups is not None:
            instance.groups.set(groups)
        instance.save()
        return instance


class GroupSerializer(serializers.Serializer):
    """Serializer para el modelo Group"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=150)
