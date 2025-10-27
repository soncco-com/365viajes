# Instrucciones para 365viajes

## Resumen

Este es un sistema de reservas para un negocio mayorista, mediante este sistema se crean itinerarios para diferentes agencias de viajes que solicitan servicios y otros para clientes, el sistema de reservas se encarga de juntar los datos y juntar servicios de modo que se atiendan a los pasajeros de acuerdo al servicio contratado, recogiendo desde un lugar específico.

## Estructura

- Django - Rest para backend
- Quasar - Vue 3 para frontend

## Instrucciones de desarrollo

## Generales

- El código debe ser legible, documentado y simple. Se debe usar los patrones de diseño y programación que permitan simplicidad y codigo legible.
- Si hay posibilidad de modularizar algúna funcionalidad se debe hacer, de modo que se pueda reusar código y evitar la duplicidad.
- Si hay funciones o mixins, se deben separar para usarlas desde cualquier lugar del código.
- No se debe agregar funcionalidades o código no especificado.
- Instalar paquetes necesarios (pip o npm) si se necesita, en sus últimas versiones.
- Podrías crear documentos de resumen en la carpeta docs y separarlos de acuerdo al entorno (back, front)

### Backend

- Funciona como un backend que sirve api endpoints que son usadas desde el frontend
- Usa rest_framework_simplejwt para el manejo de usuarios
- Los endpoint names son nombres entendibles y relacionados a sus modelos y acciones, usando - o \_ (sólo uno de ellos de acuerdo a lo que sugiera la IA)
- Cada creación, edición, eliminación en un modelo está documentado, de modo que se pueda hacer auditoria de las acciones sobre un modelo, usar una tabla específica o registros nuevos. (La IA sugiere). Esta auditoría deberá ser afinada de modo que no consuma recursos al hacer tantos registros.
- El acceso al sistema se realiza mediante los usuarios y grupos de django
- El backend debe tener una tabla donde se guarden opciones generales del sistema (Nombre de la empresa, direccion, telefonos, etc), estas opciones podrían ser públicas (sin login) o privadas (con login) de modo que se puedan usar en partes que el front no está manejando usuarios.
- Usa caché mediante redis, el caché debe implementarse de modo que se haga caché inteligente para evitar sobrecarga del sistema.
- Usa consultas optimizadas usando funciones prefetch de django
- Los reportes PDF se generan mediante weasyprint con templates y deben estar centralizados y el código de generación debe ser reusable y modularizado.
- Todos los PDF manejan una cabecera común con un logo en static y el nombre de la agencia. Los PDF podrían ser portrait o landscape, según se demande.
- Los resultados de los endpoints deben usar paginación, ordenación y búsqueda según sea necesario.
- Documentar los API endpoints.

### Frontend

- El frontend consume los datos del backend mediante el token y refresh generado por el backend
- El diseño es simple, moderno e intuitivo
- El diseño es completamente responsivo
- El diseño tiene una paleta de colores única y cambiable, y se debe respetar la paleta
- Usa navegación entendible
- El menú es superior no fijo que usa dropdowns para su navegación
- El sistema tiene un pie de página no fijo que contiene datos simples de las opciones generales del sistema.
- Se obtienen reportes PDF desde el backend y se muestran mediante dialogs, los pdf se muestran usando pdf.js y permiten zoom, impresión y descarga.
- Se deben crear y usar componentes reusables (títulos, botones, tablas, autocompletables, listados, Datepicker con input, DateRange, etc.)
- Se deben crear y usar composables para usos evitar duplicidad de funcionalidades.
- Todas las páginas usan un patrón similar usando títulos, secciones, columnas, según requiera el diseño
- Las tablas deben ser ordenables, paginadas y filtrables.
- Las páginas y menus del sistema se manejar de acuerdo a los grupos de django que provee el backend.
- El frontend usa caché para evitar llamados repetidos.
- El frontend tiene un sistema centralizado de notificaciones.
- Cuando se usen rangos de fechas en filtros estos deben ser de la siguiente manera para mandar al backend:

- Desde
- Hasta

Si sólo se establece Desde, entonces se filtra la fecha asi: fecha\_\_gte=desde
Si sólo se establece Hasta, entonces se filtra la fecha asi: fecha\_\_lte=hasta
Si ambos están establecidos, entonces se filtra la fecha asi: fecha\_\_range=desde,hasta

- Usar los beneficios de los componentes y utils de quasar siempre que se pueda.

## Páginas y funcionamiento del sistema

Las siguientes instrucciones especifican como se ve el frontend y las acciones que hace el backend.

### Estructura del menú

Se muestra la estructura, con el nombre y el acceso: Nombre (Acceso)

1. Reservas (Todos)
   1.1 Lista de reservas (Todos)
   1.2 Crear reserva (Todos)
2. Informes (Todos)
   2.1 Servicio por agencias (Todos)
   2.2 Biblia digital (Todos)
   2.3 Informe de adicionales (Todos)
   2.4 Ordenes de servicio (Todos)
   2.5 Rendición de ventas (Grupo Administrador)
3. Biblia digital (Todos) (Lo mismo que 2.2)
4. Gastos (Todos)
5. Administración (Todos)
   5.1 Usuarios (Grupo Administrador)
   5.2 Adicionales (Grupo Administrador)
   5.3 Agencias (Todos)
   5.4 Guías (Grupo Administrador)
   5.5 Horarios (Grupo Administrador)
   5.6 Hoteles (Todos)
   5.7 Servicios (Grupo Administrador)
   5.8 Transportes (Grupo Administrador)

6. Auditoría (Grupo Administrador)

Dentro del menú mostrar el Usuario actual y la posibilidad de cerrar su sesión.

## Funcionamiento del sistema

Se describe el funcionamiento de acuerdo a las páginas del menú

### 1.1 Lista de reservas

La página muestra tabla filtrable, paginada y ordenable que muestra las reservas con las siguientes columnas:

- ID = reserva.id
- Agencia = reserva.cliente.nombre
- Fecha de reserva = reserva.fecha
- Fecha de primer tour = reserva.reservadetalle[0].cuando
- Pasajero = reserva.pasajero
- Total = reserva.total
- Estado = reserva.estado_display
- Documento = reserva.documento_display
- Girado por = reserva.girado_por.first_name
- Pagado = reserva.tipo_pago_display
- Numero recibo = reserva.numero
- Número factura = reserva.numero_factura
- Acciones: Dropdown: Ver o editar la reserva, Imprimir reserva. Posibilidad de agregar más acciones.

Filtros:

ID, Agencia, Fecha de reserva (Rango de fechas), Fecha primer tour (Rango de fechas), Pasajero, Total, Estado, Documento, Girado por, Pago, Número Recibo, Número de factura.

La tabla además debe mostrar un total sumado con los totales del filtro actual.

La página además permite ir a crear reserva mediante un botón Crear Reserva

### 1.2 Crear reserva

La página es un formulario que guardará su información en el modelo Reserva, ReservaDetalle y Adicionales con los siguientes campos:

Campos para master

| Campo             | Tipo de componente                      | Campo en backend       | Datos |
| ----------------- | --------------------------------------- | ---------------------- | ----- |
| Agencia           | Autocompletable base.Cliente en backend | Reserva.cliente        |
| Estado            | q-select                                | Reserva.estado         |
| Tipo de pago      | q-select                                | Reserva.tipo_pago      |
| Pasajero          | q-input                                 | Reserva.pasajero       |
| Tipo de Documento | q-select                                | Reserva.tipo_documento |
| Observaciones     | q-input                                 | Reserva.observaciones  |

En el caso de que la agencia no exista debe permitirme crear una agencia desde un dialog.

Campos para detail de Servicio

| Campo    | Componente                                                                                                                   | Campo en backend          | Datos |
| -------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ----- |
| N. Pax   | q-input numérico entero                                                                                                      | ReservaDetalle.numero_pax | -     |
| Servicio | Autocompletable de base.Servicio en backend                                                                                  | ReservaDetalle.servicio   | -     |
| Hotel    | Autocompletable de base.Lugar en backend                                                                                     | ReservaDetalle.recoger_en | -     |
| Idioma   | q-select                                                                                                                     | ReservaDetalle.idioma     | -     |
| Fecha    | DatePicker                                                                                                                   | ReservaDetalle.cuando     | -     |
| Subtotal | q-input que calcula el numero de pax \* precio del Servicio escogido, es editable ya que el usuario si desea puede cambiarlo | ReservaDetalle.total      | -     |

Se puede agregar o quitar estos campos a demanda, ya que puede haber 0, 1 o muchos detalles de Servicios.

Campos detail de Adicionales

| Campo     | Componente                                                                | Campo en backend                  | Datos |
| --------- | ------------------------------------------------------------------------- | --------------------------------- | ----- |
| Cantidad  | q-input numérico entero                                                   | ReservaAdicionalDetalle.cantidad  | -     |
| Adicional | Autocompletable de base.Adicional                                         | ReservaAdicionalDetalle.adicional | -     |
| Cuando    | Datepicker                                                                | ReservaAdicionalDetalle.cuando    | -     |
| Subtotal  | q-input readonly que calcula la cantidad \* precio del Adicional escogido | ReservaAdicionalDetalle.total     | -     |

Se puede agregar o quitar estos campos a demanda, ya que puede haber 0, 1 o muchos detalles de Adicionales.

Mientras se llenan los formularios se actualiza un total general que es la suma de los subtotales. Este total se guarda en Reserva.total

Algunos adicionales tienen el campo llamado "Contable" como falso, entonces no se consideran se restan del total general, y se muestra la suma de estos como "Total no Contable".

Entonces total sería Total sumado - Total No Contables.

En los campos Autocompletables considerar si existe el campo "Activo" de modo que se filtren sólo los activos.

### 1.3 Editar Reserva (No está en el menú)

Mediante un ID usa los mismos campos que se pidieron en Crear Reserva, con los datos obtenidos del backend, esta página permite cambiar datos de una reserva en general.

### Consideraciones para Crear y Editar Reserva

Al guardar la reserva sea creada o editada, cuando el campo Estado es igual a Cancelado (0) entonces en el backend hacemos lo siguiente.

Si la reserva.numero is None or '' entonces asignamos a reserva.numero el valor más max + 1 de todos los números de reserva y reserva.girado = request.user

Si reserva.girado_cuando is None entonces reserva.girado_cuando = now()

Al crear la reserva master también se crean los detalles de servicios y adicionales si existieran.

Al editar la reserva master se editan, quitan o crean también detalles de servicios y adicionales, la edición no elimina los anteriores, sino los conserva sino tuvieran cambios. Si tuvieran cambios se cambian los datos.

### 2.1 Servicio por agencias

Es un formulario que pide los siguientes datos:

Agencia, rango de fechas y estado (Deuda, Cancelado)

El resultado de enviar el formulario se muestra en dos tablas simples.

Se muestran todos los ReservaDetalle o ReservaAdicionalDetalle con sus datos respectivos que coincidan con el filtro. Donde Agencia filtra Reserva.cliente, y el rango de fechas filtra Reserva.fecha, y estado filtra Reserva.estado.

Se muestra además la suma de detalles cancelados o con deuda.

Luego de mostrar el reporte, este se puede imprimir en formato PDF.

La finalidad de este informe es ver si una agencia ha pagado o aun mantiene deudas.

### 2.2 Biblia digital

Es un formulario que pide los siguientes datos:

Autocomplete de base.Servicio activo, un DatePicker y un combo de idiomas (Todos los idiomas, Español, Inglés, Bilingüe, esto es estático pero se define en reservas.models.IDIOMAS)

El filtro busca en ReservaDetalle y muestra los datos en una tabla simple, con énfasis en el nombre del psajero y el ID de la Reserva.

Hace un conteo de los pasajeros (ReservaDetalle.pax) y los suma.

Luego de mostrar el reporte se puede imprimir en formato PDF.

Además de mostrar los datos, se tiene la posibilidad de seleccionar cada fila y con la selección se puede crear una Orden de Servicio.

Antes de crear la orden de servicio, se pide también en otro formulario los siguientes datos:

Autocomplete de base.Chofer activos y Autocomplete de Base.Guia activos.

Estos pasos se podrían mostrar en un Q-stepper.

Luego se crea la orden de servicio que crea datos dentro de la tabla reservas.OrdenServicio y reservas.OrdenServicioDetalle

Por otro lado cuando se crea la orden de servicio con alguno de los ReservaDetalle escogidos, se actualiza el campo ReservaDetalle.seleccionado a True

Si al hacer el filtro inicial alguno de los ReservaDetalle.seleccionado == True, entonces la fila se muestar de otro color y no se puede seleccionar.

### 2.3 Informe de Adicionales

Es un formulario con los siguientes campos:

Autocomplete de base.Adicional activo y un Date Range.

El filtro busca en ReservaAdicionalDetalle y muestra los campos en una tabla simple, y un resumen del total.

Luego de mostrar el reporte se puede imprimir en PDF.

### 2.4 Ordenes de Servicio

Es una tabla filtrable y ordenable y paginada con las siguientes columnas que vienen de reservas.OrdenServicio

- ID = OrdenServicio.id
- Num Pasajeros = Suma de todos los OrdenServicioDetalle.referencia.num_pax
- Servicio = OrdenServicio.servicio.nombre
- Fecha = OrdenServicio.fecha
- Idioma = OrdenServicio.idioma
- Transporte = OrdenServicio.chofer.nombre
- Guia = OrdenServicio.guia.nombre
- Acciones: Un dropdown con las opciones:
  - Ver o editar
  - Imprimir con agencia (PDF de la Orden con la columna OrdenServicioDetalle.referencia.pertenece_a.agencia.nombre)
  - Imprimir sin agencia (PDF de la Orden sin agencia)
  - Eliminar: Elimina la orden y restaura los ReservaDetalle.seleccionado a False. Se debe confirmar la eliminación.

### 2.4.1 Editar Orden de SErvicio (No está en el menú)

Permite editar los datos de la orden de servicio (Sólo Guia y Transporte) los demás campos son sólo de Vista y quitar OrdenServicioDetalle, al quitar la OrdenServicioDetalle se restaura el campo ReservaDetalle.seleccionado a False respectivamente.

También desde esta misma página puedo Imprimir con agencia, Imprimir sin agencia o Eliminar la orden como describí en 2.4

### 2.5 Rendición de ventas

Es un formulario con los siguientes campos:

- Autocomplete de User activo con firstname
- Autocomplete de base.Cliente activo con el label Agencia.
- QSelect estático con tipos de Pago (Efectivo, Depósito) estos se definene en Reserva.PAGOS
- DatePicker

Esto filtra en reservas.Reserva de modo que se pueda saber que y cuanto ha cobrado cada usuario.

Luego de mostrar el reporte se puede imprimir.

### 4 Gastos

Una tabla filtrable, ordenable y paginada de reservas.Gasto

Muestra sus campos y muestra una suma de los gastos del filtro actual.

Cada usuario que no es administrador sólo puede ver sus gastos.

Se filtra por Gasto.fecha y Gasto.creado_por

### 5 Administración

Esto permite hacer un listado, creación y edición de esas entidades, todas se encuentran en el app base del backend.

Cada listado debe ser paginado, filtrable y ordenable de acuerdo a sus campos.

Las creaciones y ediciones deben usar campos autocompletables si tienen relaciones.

En el caso de usuarios también se podría cambiar la contraseña del usuario.

### 6. Auditoria

Una página o páginas que me permitan auditar o mostrar la historia de cambios, creaciones, ediciones o eliminaciones.

Esto sólo será accedido por un Administrador
