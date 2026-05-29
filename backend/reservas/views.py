"""
ViewSets para el app reservas
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q, Max, F, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from .models import Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, OrdenServicioDetalle, Gasto
from types import SimpleNamespace
from base.models import Auditoria, OrdenServicioColumna, COLUMNAS_DEFECTO
from .serializers import (
    ReservaSerializer, ReservaDetalleSerializer, ReservaAdicionalDetalleSerializer,
    OrdenServicioSerializer, OrdenServicioDetalleSerializer, GastoSerializer
)
from base.utils.pdf_generator import PDFGenerator


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Reservas con lógica de negocio especial
    """
    queryset = Reserva.objects.select_related(
        'cliente', 'creado_por', 'girado_por'
    ).prefetch_related(
        'reservadetalle_set__servicio',
        'reservadetalle_set__recoger_en',
        'reservaadicionaldetalle_set__adicional'
    ).all()
    serializer_class = ReservaSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'id': ['exact'],
        'cliente': ['exact'],
        'estado': ['exact'],
        'tipo_documento': ['exact'],
        'tipo_pago': ['exact'],
        'fecha': ['exact', 'gte', 'lte', 'range'],
        'girado_por': ['exact'],
        'girado_cuando': ['exact', 'gte', 'lte', 'date'],
    }
    search_fields = ['pasajero', 'numero', 'numero_factura', 'observaciones']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def get_queryset(self):
        qs = super().get_queryset()
        numero_rango = self.request.query_params.get('numero_rango')
        if numero_rango:
            try:
                parts = numero_rango.split('-')
                if len(parts) == 2:
                    start, end = int(parts[0]), int(parts[1])
                    if start <= end <= start + 1000:
                        numeros = [str(i) for i in range(start, end + 1)]
                        qs = qs.filter(numero__in=numeros)
                else:
                    qs = qs.filter(numero=numero_rango)
            except (ValueError, IndexError):
                pass
        return qs

    def destroy(self, request, *args, **kwargs):
        """
        Evitar la eliminación de reservas que tengan detalles asociados a órdenes de servicio
        """
        reserva = self.get_object()

        # Verificar si algún detalle de la reserva está en una orden de servicio
        detalles_en_ordenes = OrdenServicioDetalle.objects.filter(
            referencia__pertenece_a=reserva
        ).exists()

        if detalles_en_ordenes:
            return Response(
                {
                    'error': 'No se puede eliminar la reserva porque tiene servicios asociados a órdenes de servicio. '
                             'Elimine primero las órdenes de servicio relacionadas.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Al crear, aplicar lógica de estado Pagado"""
        reserva = serializer.save()
        self._aplicar_logica_estado(reserva)

    def perform_update(self, serializer):
        """Al actualizar, aplicar lógica de estado Pagado"""
        reserva = serializer.save()
        self._aplicar_logica_estado(reserva)

    def _aplicar_logica_estado(self, reserva):
        """
        Si estado='0' (Pagado):
        - Asignar número (max+1) si no tiene
        - Asignar girado_por y girado_cuando si no tiene
        """
        if reserva.estado == '0':  # Pagado
            if not reserva.numero:
                max_numero = Reserva.objects.filter(numero__isnull=False).aggregate(
                    max_num=Max('numero')
                )['max_num']
                try:
                    nuevo_numero = int(max_numero) + 1 if max_numero else 1
                except:
                    nuevo_numero = 1
                reserva.numero = str(nuevo_numero)

            if not reserva.girado_cuando:
                reserva.girado_cuando = timezone.now()

            reserva.save()

    @action(detail=False, methods=['get'])
    def pdf_rendicion_ventas(self, request):
        """Genera PDF de la rendición de ventas"""
        usuario_id = request.query_params.get('girado_por')
        fecha_desde = request.query_params.get('girado_cuando__gte')
        fecha_hasta = request.query_params.get('girado_cuando__lte')
        agencia_id = request.query_params.get('cliente')
        tipo_pago = request.query_params.get('tipo_pago')

        if not usuario_id or not fecha_desde or not fecha_hasta:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        from django.contrib.auth.models import User
        from base.models import Cliente

        usuario = User.objects.get(id=usuario_id)
        agencia = Cliente.objects.get(id=agencia_id) if agencia_id else None

        # Filtrar reservas pagadas (estado='0')
        reservas_qs = self.get_queryset().filter(
            estado='0',
            girado_por_id=usuario_id,
            girado_cuando__gte=fecha_desde,
            girado_cuando__lte=fecha_hasta
        )
        if agencia_id:
            reservas_qs = reservas_qs.filter(cliente_id=agencia_id)
        if tipo_pago is not None:
            reservas_qs = reservas_qs.filter(tipo_pago=tipo_pago)

        # Crear lista con campos necesarios para el template
        reservas = []
        for r in reservas_qs:
            # Calcular fecha del primer servicio
            primer_servicio = r.reservadetalle_set.order_by(
                'cuando').values_list('cuando', flat=True).first()

            reservas.append({
                'id': r.id,
                'numero': r.numero,
                'cliente_nombre': r.cliente.nombre if r.cliente else '',
                'fecha_primer_servicio': primer_servicio,
                'girado_cuando': r.girado_cuando,
                'pasajero': r.pasajero,
                'tipo_documento_display': r.get_tipo_documento_display(),
                'tipo_pago_display': r.get_tipo_pago_display() if r.tipo_pago else None,
                'total': r.total,
            })

        total_general = sum(float(r['total'] or 0) for r in reservas)

        tipo_pago_map = {'0': 'Efectivo', '1': 'Depósito', '2': 'Otro'}

        context = {
            'usuario_nombre': usuario.get_full_name() or usuario.username,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'agencia_nombre': agencia.nombre if agencia else None,
            'tipo_pago_display': tipo_pago_map.get(tipo_pago) if tipo_pago else None,
            'reservas': reservas,
            'total_general': total_general,
        }

        pdf_gen = PDFGenerator('pdf/rendicion_ventas.html',
                               context, orientation='portrait')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="rendicion_ventas_{usuario.username}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def totales(self, request):
        """Calcula totales de las reservas filtradas"""
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.aggregate(total=Sum('total'))['total'] or 0
        total_nocontable = queryset.aggregate(
            total=Sum('total_nocontable'))['total'] or 0

        return Response({
            'total': total,
            'total_nocontable': total_nocontable,
            'total_neto': total - total_nocontable,
            'cantidad': queryset.count()
        })

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """
        Obtiene el historial completo de cambios de una reserva
        Incluye cambios en la reserva, sus detalles y adicionales
        Solo accesible por administradores
        """
        reserva = self.get_object()

        # Verificar que sea administrador
        if not request.user.groups.filter(name='Administrador').exists():
            return Response(
                {'error': 'Solo los administradores pueden ver el historial'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener ContentTypes
        ct_reserva = ContentType.objects.get_for_model(Reserva)
        ct_detalle = ContentType.objects.get_for_model(ReservaDetalle)
        ct_adicional = ContentType.objects.get_for_model(
            ReservaAdicionalDetalle)

        # Obtener IDs de detalles y adicionales de esta reserva
        detalles_ids = list(
            reserva.reservadetalle_set.values_list('id', flat=True))
        adicionales_ids = list(
            reserva.reservaadicionaldetalle_set.values_list('id', flat=True))

        # Obtener todas las auditorías relacionadas
        auditorias = Auditoria.objects.filter(
            # Cambios en la reserva
            Q(content_type=ct_reserva, object_id=reserva.id) |
            # Cambios en detalles
            Q(content_type=ct_detalle, object_id__in=detalles_ids) |
            # Cambios en adicionales
            Q(content_type=ct_adicional, object_id__in=adicionales_ids)
        ).select_related('usuario', 'content_type').order_by('-fecha')

        # Serializar resultados
        historial_data = []
        for auditoria in auditorias:
            historial_data.append({
                'id': auditoria.id,
                'fecha': auditoria.fecha,
                'usuario': auditoria.usuario.username,
                'usuario_nombre_completo': f"{auditoria.usuario.first_name} {auditoria.usuario.last_name}".strip() or auditoria.usuario.username,
                'accion': auditoria.accion,
                'accion_display': auditoria.get_accion_display(),
                'modelo': str(auditoria.content_type.model).title(),
                'modelo_id': auditoria.object_id,
                'datos_anteriores': auditoria.datos_anteriores,
                'datos_nuevos': auditoria.datos_nuevos,
                'ip_address': auditoria.ip_address,
            })

        return Response({
            'reserva_id': reserva.id,
            'reserva_numero': reserva.numero,
            'pasajero': reserva.pasajero,
            'historial': historial_data,
            'total_cambios': len(historial_data)
        })

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):  # pylint: disable=unused-argument
        """Genera PDF de la reserva"""
        reserva = self.get_object()

        # Cargar detalles y adicionales con relaciones
        detalles = reserva.reservadetalle_set.select_related(
            'servicio', 'recoger_en').all()
        adicionales = reserva.reservaadicionaldetalle_set.select_related(
            'adicional').all()

        # Calcular total neto
        total_neto = float(reserva.total) - float(reserva.total_nocontable)

        context = {
            'reserva': reserva,
            'detalles': detalles,
            'adicionales': adicionales,
            'total_neto': total_neto,
        }

        pdf_gen = PDFGenerator(
            'pdf/reserva.html', context, orientation='portrait')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="reserva_{reserva.id}.pdf"'
        return response


class ReservaDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para ver detalles de reservas
    Usado principalmente para reportes
    """
    queryset = ReservaDetalle.objects.select_related(
        'pertenece_a__cliente',
        'servicio',
        'recoger_en'
    ).all()
    serializer_class = ReservaDetalleSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'pertenece_a': ['exact'],
        'servicio': ['exact'],
        'cuando': ['exact', 'gte', 'lte', 'range'],
        'idioma': ['exact'],
        'seleccionado': ['exact'],
        'pertenece_a__cliente': ['exact'],
        'pertenece_a__estado': ['exact'],
    }
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def pdf_servicio_agencias(self, request):
        """Genera PDF del informe de servicios por agencia (agrupado por reserva)"""
        # Obtener parámetros
        fecha_range = request.query_params.get('cuando__range', '')
        if ',' in fecha_range:
            fecha_desde, fecha_hasta = fecha_range.split(',', 1)
        else:
            fecha_desde = request.query_params.get('cuando__gte')
            fecha_hasta = request.query_params.get('cuando__lte')
        cliente_id = request.query_params.get('pertenece_a__cliente')
        estado = request.query_params.get('pertenece_a__estado')

        if not fecha_desde or not fecha_hasta or not cliente_id:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        from base.models import Cliente
        cliente = Cliente.objects.get(id=cliente_id)

        # Obtener IDs de reservas con servicios o adicionales en el rango
        servicio_reserva_ids = set(
            ReservaDetalle.objects.filter(
                cuando__gte=fecha_desde, cuando__lte=fecha_hasta,
                pertenece_a__cliente_id=cliente_id
            ).values_list('pertenece_a_id', flat=True)
        )
        adicional_reserva_ids = set(
            ReservaAdicionalDetalle.objects.filter(
                cuando__gte=fecha_desde, cuando__lte=fecha_hasta,
                pertenece_a__cliente_id=cliente_id
            ).values_list('pertenece_a_id', flat=True)
        )
        all_reserva_ids = servicio_reserva_ids | adicional_reserva_ids

        # Reservas con prefetch filtrado al rango de fechas
        reservas_qs = Reserva.objects.filter(id__in=all_reserva_ids).prefetch_related(
            Prefetch(
                'reservadetalle_set',
                queryset=ReservaDetalle.objects.filter(
                    cuando__gte=fecha_desde, cuando__lte=fecha_hasta
                ).select_related('servicio'),
            ),
            Prefetch(
                'reservaadicionaldetalle_set',
                queryset=ReservaAdicionalDetalle.objects.filter(
                    cuando__gte=fecha_desde, cuando__lte=fecha_hasta
                ).select_related('adicional'),
            ),
        )
        if estado:
            reservas_qs = reservas_qs.filter(estado=estado)

        # Construir datos agrupados por reserva
        reservas_data = []
        total_general = 0
        total_pagado = 0
        total_deuda = 0

        for r in reservas_qs.order_by('id'):
            servicios_lines = []
            subtotal_servicios = 0
            for d in r.reservadetalle_set.all():
                nombre = d.servicio.nombre if d.servicio else ''
                fecha = d.cuando.strftime('%d/%m/%Y')
                precio_unit = float(d.precio_aplicado) if d.precio_aplicado else (
                    float(d.servicio.precio) if d.servicio else 0)
                servicios_lines.append(
                    f"{d.numero_pax} x {nombre} ({fecha}) ({precio_unit:.2f}) {float(d.total):.2f}"
                )
                subtotal_servicios += float(d.total or 0)

            adicionales_lines = []
            subtotal_adicionales = 0
            for a in r.reservaadicionaldetalle_set.all():
                nombre = a.adicional.nombre if a.adicional else ''
                fecha = a.cuando.strftime('%d/%m/%Y')
                precio_unit = float(a.precio_aplicado) if a.precio_aplicado else (
                    float(a.adicional.precio) if a.adicional else 0)
                adicionales_lines.append(
                    f"{a.cantidad} x {nombre} ({fecha}) ({precio_unit:.2f}) {float(a.total):.2f}"
                )
                subtotal_adicionales += float(a.total or 0)

            subtotal = subtotal_servicios + subtotal_adicionales
            total_general += subtotal
            if r.estado == '0':
                total_pagado += subtotal
            else:
                total_deuda += subtotal

            reservas_data.append({
                'id': r.id,
                'pasajero': r.pasajero,
                'servicios': '\n'.join(servicios_lines),
                'adicionales': '\n'.join(adicionales_lines),
                'subtotal': subtotal,
                'numero': r.numero or '',
                'estado': r.get_estado_display(),
            })

        from datetime import datetime

        def _fmt(s):
            try:
                return datetime.strptime(s, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                return s

        context = {
            'cliente_nombre': cliente.nombre,
            'fecha_desde': _fmt(fecha_desde),
            'fecha_hasta': _fmt(fecha_hasta),
            'estado_filter': dict([('0', 'Pagado'), ('1', 'Deuda')]).get(estado) if estado else None,
            'reservas': reservas_data,
            'total_general': total_general,
            'total_pagado': total_pagado,
            'total_deuda': total_deuda,
        }

        pdf_gen = PDFGenerator('pdf/servicio_agencias.html',
                               context, orientation='portrait', include_header=False)
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="servicios_agencias_{cliente.nombre}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def biblia_digital(self, request):
        """
        Reporte Biblia Digital
        Devuelve detalles de reservas para crear órdenes de servicio
        """
        queryset = self.get_queryset().prefetch_related(
            'pertenece_a__reservaadicionaldetalle_set__adicional'
        )

        # Filtros
        servicio_id = request.query_params.get('servicio')
        fecha_gte = request.query_params.get('fecha__gte')
        fecha_lte = request.query_params.get('fecha__lte')
        fecha_range = request.query_params.get('fecha__range')
        seleccionado = request.query_params.get('seleccionado')
        idioma = request.query_params.get('idioma')

        if servicio_id:
            queryset = queryset.filter(servicio_id=servicio_id)

        if idioma:
            queryset = queryset.filter(idioma=idioma)

        if fecha_range:
            # formato: "fecha_desde,fecha_hasta"
            fechas = fecha_range.split(',')
            if len(fechas) == 2:
                queryset = queryset.filter(
                    cuando__range=[fechas[0], fechas[1]])
        else:
            if fecha_gte:
                queryset = queryset.filter(cuando__gte=fecha_gte)
            if fecha_lte:
                queryset = queryset.filter(cuando__lte=fecha_lte)

        if seleccionado is not None:
            is_selected = seleccionado.lower() == 'true'
            queryset = queryset.filter(seleccionado=is_selected)

        # Paginación y ordenamiento
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        ordering = request.query_params.get('ordering', '-cuando')

        # Mapear campos de ordenamiento a campos del modelo
        ordering_map = {
            'cuando': 'cuando',
            'reserva_fecha': 'pertenece_a__fecha',
            'reserva_numero': 'pertenece_a__numero',
            'cliente_nombre': 'pertenece_a__cliente__nombre',
            'pasajero': 'pertenece_a__pasajero',
            'servicio_nombre': 'servicio__nombre',
            'lugar_nombre': 'recoger_en__nombre',
            '-cuando': '-cuando',
            '-reserva_fecha': '-pertenece_a__fecha',
            '-reserva_numero': '-pertenece_a__numero',
            '-cliente_nombre': '-pertenece_a__cliente__nombre',
            '-pasajero': '-pertenece_a__pasajero',
            '-servicio_nombre': '-servicio__nombre',
            '-lugar_nombre': '-recoger_en__nombre',
        }

        # Aplicar ordenamiento mapeado
        ordering_field = ordering_map.get(ordering, ordering)
        queryset = queryset.order_by(ordering_field)

        # Contar total
        total_count = queryset.count()

        # Aplicar paginación
        start = (page - 1) * page_size
        end = start + page_size
        queryset = queryset[start:end]

        # Serializar con datos adicionales
        results = []
        for detalle in queryset:
            results.append({
                'id': detalle.id,
                'reserva_id': detalle.pertenece_a.id,
                'reserva_numero': detalle.pertenece_a.numero,
                'reserva_fecha': detalle.pertenece_a.fecha,
                'cliente_id': detalle.pertenece_a.cliente.id if detalle.pertenece_a.cliente else None,
                'cliente_nombre': detalle.pertenece_a.cliente.nombre if detalle.pertenece_a.cliente else '',
                'pasajero': detalle.pertenece_a.pasajero,
                'servicio_id': detalle.servicio.id,
                'servicio_nombre': detalle.servicio.nombre,
                'lugar_id': detalle.recoger_en.id if detalle.recoger_en else None,
                'lugar_nombre': detalle.recoger_en.nombre if detalle.recoger_en else '',
                'cuando': detalle.cuando,
                'numero_pax': detalle.numero_pax,
                'subtotal': float(detalle.total) if detalle.total else 0.0,
                'idioma': detalle.idioma,
                'seleccionado': detalle.seleccionado,
                'destino': detalle.destino,
                'tipo_documento': detalle.pertenece_a.tipo_documento,
                'tipo_documento_display': detalle.pertenece_a.get_tipo_documento_display(),
                'observaciones_reserva': detalle.pertenece_a.observaciones or '',
                'estado': detalle.pertenece_a.estado,
                'estado_display': detalle.pertenece_a.get_estado_display(),
                'girado_por': detalle.pertenece_a.girado_por.username if detalle.pertenece_a.girado_por else '',
                'adicionales': '\n'.join(
                    f"{ad.adicional.nombre} x{ad.cantidad}"
                    for ad in detalle.pertenece_a.reservaadicionaldetalle_set.all()
                ),
            })

        return Response({
            'count': total_count,
            'next': None,
            'previous': None,
            'results': results
        })


class ReservaAdicionalDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para detalles de adicionales"""
    queryset = ReservaAdicionalDetalle.objects.select_related(
        'pertenece_a__cliente',
        'adicional'
    ).all()
    serializer_class = ReservaAdicionalDetalleSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'pertenece_a': ['exact'],
        'adicional': ['exact'],
        'cuando': ['exact', 'gte', 'lte', 'range'],
        'pertenece_a__cliente': ['exact'],
        'pertenece_a__estado': ['exact'],
    }
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def pdf_adicionales(self, request):
        """Genera PDF del informe de adicionales"""
        fecha_range = request.query_params.get('cuando__range', '')
        if ',' in fecha_range:
            fecha_desde, fecha_hasta = fecha_range.split(',', 1)
        else:
            fecha_desde = request.query_params.get('cuando__gte')
            fecha_hasta = request.query_params.get('cuando__lte')
        adicional_id = request.query_params.get('adicional')

        if not fecha_desde or not fecha_hasta or not adicional_id:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        from base.models import Adicional
        adicional = Adicional.objects.get(id=adicional_id)

        adicionales_qs = self.get_queryset().filter(
            cuando__gte=fecha_desde,
            cuando__lte=fecha_hasta,
            adicional_id=adicional_id
        ).select_related('pertenece_a', 'adicional')

        # Crear lista con campos necesarios para el template
        adicionales = []
        for a in adicionales_qs:
            adicionales.append({
                'cuando': a.cuando,
                'reserva_id': a.pertenece_a.id,
                'reserva_pasajero': a.pertenece_a.pasajero,
                'adicional_nombre': a.adicional.nombre if a.adicional else '',
                'cantidad': a.cantidad,
                'adicional_precio': float(a.precio_aplicado) if a.precio_aplicado else (float(a.adicional.precio) if a.adicional else 0),
                'adicional_contable': a.adicional.contable if a.adicional else True,
                'total': a.total,
            })

        # Calcular totales
        cantidad_total = sum(a['cantidad'] for a in adicionales)
        total_contable = sum(float(a['total'] or 0)
                             for a in adicionales if a['adicional_contable'])
        total_no_contable = sum(float(a['total'] or 0)
                                for a in adicionales if not a['adicional_contable'])
        total_general = total_contable + total_no_contable

        context = {
            'adicional_nombre': adicional.nombre,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'cantidad_total': cantidad_total,
            'adicionales': adicionales,
            'total_contable': total_contable,
            'total_no_contable': total_no_contable,
            'total_general': total_general,
        }

        pdf_gen = PDFGenerator(
            'pdf/adicionales_reporte.html', context, orientation='portrait')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="adicionales_{adicional.nombre}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def informe(self, request):
        """Informe de adicionales con totales"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        total = queryset.aggregate(total=Sum('total'))['total'] or 0

        return Response({
            'detalles': serializer.data,
            'total': total
        })


class OrdenServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Órdenes de Servicio
    Al eliminar, restaura seleccionado=False en ReservaDetalle
    """
    queryset = OrdenServicio.objects.select_related(
        'servicio', 'guia', 'chofer', 'responsable'
    ).prefetch_related(
        'ordenserviciodetalle_set__referencia__pertenece_a'
    ).all()
    serializer_class = OrdenServicioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio', 'fecha',
                        'idioma', 'guia', 'chofer', 'responsable']
    search_fields = ['servicio__nombre', 'guia__nombre',
                     'chofer__nombre', 'responsable__nombre']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def perform_destroy(self, instance):
        """Al eliminar, restaurar seleccionado=False en detalles"""
        for detalle in instance.ordenserviciodetalle_set.all():
            detalle.referencia.seleccionado = False
            detalle.referencia.save()
        instance.delete()

    @action(detail=True, methods=['delete'])
    def eliminar_detalle(self, request, pk=None):
        """Elimina un detalle de la orden y restaura seleccionado=False"""
        detalle_id = request.data.get('detalle_id')
        if not detalle_id:
            return Response(
                {'error': 'detalle_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            detalle = OrdenServicioDetalle.objects.get(
                id=detalle_id,
                pertenece_a_id=pk
            )
            detalle.referencia.seleccionado = False
            detalle.referencia.save()
            detalle.delete()

            return Response({'message': 'Detalle eliminado'})
        except OrdenServicioDetalle.DoesNotExist:
            return Response(
                {'error': 'Detalle no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def reordenar(self, request, pk=None):
        """Reordena los detalles de la orden según la lista de IDs recibida"""
        orden = self.get_object()
        detalle_ids = request.data.get('detalle_ids', [])
        if not detalle_ids:
            return Response(
                {'error': 'detalle_ids requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for idx, detalle_id in enumerate(detalle_ids):
            OrdenServicioDetalle.objects.filter(
                id=detalle_id, pertenece_a=orden
            ).update(sort=idx)

        return Response({'message': 'Orden actualizado'})

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        Genera PDF de la orden de servicio con columnas configurables por Servicio.
        Parámetros query:
        - mostrar_agencia: true/false (default true) — override para la columna agencia
        """
        try:
            orden = self.get_object()

            mostrar_agencia = request.query_params.get(
                'mostrar_agencia', 'true').lower() == 'true'

            # --- Columnas configuradas ---
            columnas_qs = OrdenServicioColumna.objects.filter(
                servicio=orden.servicio, visible=True
            ).order_by('orden')

            if columnas_qs.exists():
                columnas = list(columnas_qs)
            else:
                # Backward-compatible: usar columnas default si no hay config
                columnas = [SimpleNamespace(**c) for c in COLUMNAS_DEFECTO]

            # Aplicar override mostrar_agencia
            claves_visibles = {c.clave for c in columnas}
            if not mostrar_agencia:
                claves_visibles.discard('agencia')

            # --- Paradas del servicio ---
            paradas = orden.servicio.paradas.all().order_by('orden')

            # --- Adicionales de la fecha ---
            adicionales_fecha = ReservaAdicionalDetalle.objects.filter(
                cuando=orden.fecha
            ).select_related('adicional', 'pertenece_a').values(
                'pk', 'pertenece_a_id', 'adicional__nombre', 'adicional__precio',
                'adicional__visible', 'adicional__boleto', 'adicional__almuerzo',
                'cantidad'
            )

            adicionales_por_reserva = {}
            for adic in adicionales_fecha:
                rid = adic['pertenece_a_id']
                adicionales_por_reserva.setdefault(rid, []).append(adic)

            # --- Procesar detalles ---
            detalles_procesados = []
            total_pax = 0
            total_ingresos = 0
            total_almuerzos = 0
            adicionales_usados = set()

            for detalle_orden in orden.ordenserviciodetalle_set.select_related(
                'referencia__pertenece_a__cliente', 'referencia__recoger_en'
            ).all():
                reserva_detalle = detalle_orden.referencia
                reserva = reserva_detalle.pertenece_a

                adicionales = adicionales_por_reserva.get(reserva.id, [])

                ingresos_count = 0
                almuerzos_count = 0
                ingresos_list = []
                almuerzos_list = []
                otros_adicionales = []

                for adicional in adicionales:
                    if adicional['pk'] in adicionales_usados:
                        continue
                    adicionales_usados.add(adicional['pk'])

                    if not adicional['adicional__visible']:
                        continue

                    if adicional['adicional__boleto']:
                        ingresos_count += adicional['cantidad']
                        ingresos_list.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")
                    elif adicional['adicional__almuerzo']:
                        almuerzos_count += adicional['cantidad']
                        almuerzos_list.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")
                    else:
                        otros_adicionales.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")

                total_pax += reserva_detalle.numero_pax
                total_ingresos += ingresos_count
                total_almuerzos += almuerzos_count

                obs_detalle = reserva_detalle.observaciones or ''
                obs_reserva = reserva.observaciones or ''
                observaciones_final = obs_detalle if obs_detalle else obs_reserva

                # Datos por clave para el template dinámico
                detalles_procesados.append({
                    'pax': reserva_detalle.numero_pax,
                    'hotel': reserva_detalle.recoger_en.nombre if reserva_detalle.recoger_en else '',
                    'pasajero': reserva.pasajero,
                    'agencia': reserva.cliente.nombre if reserva.cliente else '',
                    'destino': reserva_detalle.destino or '',
                    'ingresos': '\n'.join(sorted(ingresos_list)) if ingresos_list else '',
                    'almuerzo': '\n'.join(sorted(almuerzos_list)) if almuerzos_list else '',
                    'adicionales': '\n'.join(sorted(otros_adicionales)) if otros_adicionales else '',
                    'observaciones': observaciones_final,
                    # totales internos para la fila de totales
                    '_ingresos_count': ingresos_count,
                    '_almuerzos_count': almuerzos_count,
                })

            context = {
                'orden': orden,
                'paradas': paradas,
                'columnas': [
                    c for c in columnas if c.clave in claves_visibles
                ],
                'detalles': detalles_procesados,
                'total_pax': total_pax,
                'total_ingresos': total_ingresos,
                'total_almuerzos': total_almuerzos,
                'mostrar_agencia': mostrar_agencia,
            }

            pdf_gen = PDFGenerator(
                'pdf/orden_servicio.html', context, orientation='portrait', include_header=False)
            pdf_bytes = pdf_gen.generate()

            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="orden_servicio_{orden.id}.pdf"'
            return response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GastoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gastos
    Los usuarios normales solo ven sus propios gastos
    """
    queryset = Gasto.objects.select_related('creado_por').all()
    serializer_class = GastoSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fecha', 'creado_por']
    search_fields = ['descripcion']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def get_queryset(self):
        """Filtrar por usuario si no es administrador"""
        queryset = super().get_queryset()
        user = self.request.user

        # Si no es administrador, solo ver sus propios gastos
        if not user.groups.filter(name='Administrador').exists():
            queryset = queryset.filter(creado_por=user)

        return queryset

    @action(detail=False, methods=['get'])
    def totales(self, request):
        """Calcula el total de gastos filtrados"""
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            'total': total,
            'cantidad': queryset.count()
        })
