"""
Serializers para el app reservas
"""
from rest_framework import serializers
from .models import Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, OrdenServicioDetalle, Gasto
from base.serializers import ClienteSerializer, ServicioSerializer, LugarSerializer, AdicionalSerializer, GuiaSerializer, ChoferSerializer


class ReservaDetalleSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)
    servicio_precio = serializers.DecimalField(
        source='servicio.precio', max_digits=11, decimal_places=2, read_only=True)
    lugar_nombre = serializers.CharField(
        source='recoger_en.nombre', read_only=True)
    idioma_display = serializers.CharField(
        source='get_idioma_display', read_only=True)

    class Meta:
        model = ReservaDetalle
        fields = '__all__'


class ReservaAdicionalDetalleSerializer(serializers.ModelSerializer):
    adicional_nombre = serializers.CharField(
        source='adicional.nombre', read_only=True)
    adicional_precio = serializers.DecimalField(
        source='adicional.precio', max_digits=11, decimal_places=2, read_only=True)
    adicional_contable = serializers.BooleanField(
        source='adicional.contable', read_only=True)

    class Meta:
        model = ReservaAdicionalDetalle
        fields = '__all__'


class ReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source='cliente.nombre', read_only=True)
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True)
    tipo_documento_display = serializers.CharField(
        source='get_tipo_documento_display', read_only=True)
    tipo_pago_display = serializers.CharField(
        source='get_tipo_pago_display', read_only=True)
    creado_por_nombre = serializers.CharField(
        source='creado_por.first_name', read_only=True)
    girado_por_nombre = serializers.CharField(
        source='girado_por.first_name', read_only=True)

    # Nested serializers para detalles
    detalles = ReservaDetalleSerializer(
        source='reservadetalle_set', many=True, read_only=True)
    adicionales_detalle = ReservaAdicionalDetalleSerializer(
        source='reservaadicionaldetalle_set', many=True, read_only=True)

    # Para escritura
    detalles_data = serializers.ListField(write_only=True, required=False)
    adicionales_data = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ['creado_por',
                            'girado_por', 'girado_cuando', 'numero']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_data', [])
        adicionales_data = validated_data.pop('adicionales_data', [])

        # Asignar el usuario que crea
        validated_data['creado_por'] = self.context['request'].user
        validated_data['girado_por'] = self.context['request'].user

        # Crear la reserva
        reserva = Reserva.objects.create(**validated_data)

        # Crear detalles de servicios
        for detalle_data in detalles_data:
            ReservaDetalle.objects.create(pertenece_a=reserva, **detalle_data)

        # Crear detalles de adicionales
        for adicional_data in adicionales_data:
            ReservaAdicionalDetalle.objects.create(
                pertenece_a=reserva, **adicional_data)

        return reserva

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles_data', None)
        adicionales_data = validated_data.pop('adicionales_data', None)

        # Actualizar campos de la reserva
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar detalles de servicios si se proporcionan
        if detalles_data is not None:
            # Eliminar detalles anteriores
            instance.reservadetalle_set.all().delete()
            # Crear nuevos detalles
            for detalle_data in detalles_data:
                ReservaDetalle.objects.create(
                    pertenece_a=instance, **detalle_data)

        # Actualizar detalles de adicionales si se proporcionan
        if adicionales_data is not None:
            # Eliminar adicionales anteriores
            instance.reservaadicionaldetalle_set.all().delete()
            # Crear nuevos adicionales
            for adicional_data in adicionales_data:
                ReservaAdicionalDetalle.objects.create(
                    pertenece_a=instance, **adicional_data)

        return instance


class OrdenServicioDetalleSerializer(serializers.ModelSerializer):
    reserva_detalle_info = ReservaDetalleSerializer(
        source='referencia', read_only=True)

    class Meta:
        model = OrdenServicioDetalle
        fields = '__all__'


class OrdenServicioSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(
        source='servicio.nombre', read_only=True)
    guia_nombre = serializers.CharField(source='guia.nombre', read_only=True)
    chofer_nombre = serializers.CharField(
        source='chofer.nombre', read_only=True)
    idioma_display = serializers.CharField(
        source='get_idioma_display', read_only=True)

    detalles = OrdenServicioDetalleSerializer(
        source='ordenserviciodetalle_set', many=True, read_only=True)
    detalles_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = OrdenServicio
        fields = '__all__'

    def create(self, validated_data):
        detalles_ids = validated_data.pop('detalles_ids', [])
        orden = OrdenServicio.objects.create(**validated_data)

        # Crear detalles y marcar como seleccionados
        for idx, detalle_id in enumerate(detalles_ids):
            reserva_detalle = ReservaDetalle.objects.get(id=detalle_id)
            reserva_detalle.seleccionado = True
            reserva_detalle.save()
            OrdenServicioDetalle.objects.create(
                pertenece_a=orden,
                referencia=reserva_detalle,
                sort=idx
            )

        return orden

    def update(self, instance, validated_data):
        detalles_ids = validated_data.pop('detalles_ids', None)

        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar detalles si se proporcionan
        if detalles_ids is not None:
            # Restaurar seleccionado=False en detalles anteriores
            for detalle in instance.ordenserviciodetalle_set.all():
                detalle.referencia.seleccionado = False
                detalle.referencia.save()

            # Eliminar detalles anteriores
            instance.ordenserviciodetalle_set.all().delete()

            # Crear nuevos detalles
            for idx, detalle_id in enumerate(detalles_ids):
                reserva_detalle = ReservaDetalle.objects.get(id=detalle_id)
                reserva_detalle.seleccionado = True
                reserva_detalle.save()
                OrdenServicioDetalle.objects.create(
                    pertenece_a=instance,
                    referencia=reserva_detalle,
                    sort=idx
                )

        return instance


class GastoSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(
        source='creado_por.first_name', read_only=True)

    class Meta:
        model = Gasto
        fields = '__all__'
        read_only_fields = ['creado_por']

    def create(self, validated_data):
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)
