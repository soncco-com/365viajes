Mejoraremos el formato de Orden de Servicio:

- el nombre de Servicio debe resaltarse de una manera muy visible.

En el caso de cada item de la tabla, antes se hacía de esta manera:

objects = []
for detalle in orden.ordenserviciodetalle_set.all():
horario = get_horario(detalle.referencia)
detalle.referencia.hora = horario['hora']
objects.append(detalle.referencia)

    servicio_formato = orden.servicio.formato
    fecha = orden.fecha

    usados = []
    total = 0
    for item in objects:
        adicionales_set = item.pertenece_a.reservaadicionaldetalle_set.filter(
            cuando=fecha)
        adicionales = []
        for detalle in adicionales_set:
            if detalle.pk not in usados:
                usados.append(detalle.pk)
                adicionales.append({
                    'pk': detalle.pk,
                    'cantidad': detalle.cantidad,
                    'nombre': detalle.adicional.nombre,
                    'precio': float(detalle.adicional.precio),
                    'visible': detalle.adicional.visible,
                    'almuerzo': detalle.adicional.almuerzo,
                    'boleto': detalle.adicional.boleto,
                })
            item.adicionales = adicionales
        total += item.numero_pax

De modo que cada item de objects muestre el servicio y sus adicionales relacionados, pero como te expliqué antes cada adicional:

Y en el caso de adicionales, un campo/columna de acuerdo a sus propiedades.

Si adicional.boleto, entonces en un lugar que dice "Ingresos"

Si adicional.almuerzo, entonces en algun lugar que diga "Almuerzo"

Si !adicional.visible, no se muestra

Podríamos usar tablas, grids, o lo necesario sin embargo la información debería caber en una sóla página.

Puedes cambiar la manera de ese algoritmo de ejemplo y mejorarlo o cambiarlo totalmente.
