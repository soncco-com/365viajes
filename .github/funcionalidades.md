# Nuevas funcionalidades

Vamos a agregar algunas nuevas funcionalidades

## Servicios

### Destino

Algunos servicios deben tener el campo booleando "Mostrar Destinos", de modo que cuando se escoja en la reserva, entonces la ReservaDetalle guarde un campo de texto llamado "Destino", que será simplemente un campo de texto simple. Esto sirve para que cuando termine un servicio, se indique donde terminará

Esto se debe reflejar en el formulario de Reserva de modo que si se escoge ese servicio se muestre el campo destino

### Precios especiales para agencias

Algunos agencias deben tener la posibilidad de tener un precio especial para sus Servicios, ejemplo

El servicio de City Tour cuesta 20 soles, pero para la agencia Tikaymi este precio será de 18 soles. Entonces el cálculo del subtotal debe hacerse con este precio.

Esto se debe guardar en alguna tabla y no debería alterar los registros de reservas pasados si es que su valor cambia o se elimina. Es sólo referencial para el cálculo.

Sin embargo, en algun lugar de la reserva debería guardarse como un informativo de por qué se usó ese precio.

Estos precios pueden estar activos o inactivos, y sólo se deben considerar si están activos.

Por otro lado en la reserva detalle, el precio total aunque es calculado debería ser editable por si el usuario actual quiere aplicar algún otro descuento.

### Itinerario/Parada

No se que nombre poner, pero cada servicio podría opcionalmente guardar en una tabla las paradas que hace.

Crear un modelo específico y el Servicio podría tener lo que se muestra en este ejemplo:

Servicio: Valle Sagrado

Paradas: Pisac, Urubamba, Ollantaytambo, Chinchero

No todos los servicios tendrán paradas

Escoger el nombre de modelo que mejor se ajuste

## Reservas

Mejorar el diseño de los Servicios y Adicionales, esteos deberían verse y llenarse de mejor manera tanto en web como en mobiles, Talvez se debería usar grids en vez de tablas.

Escoge lo que mejor se adapte, pero sin perder las funcionalidades de cálculos, eliminación, etc.
