"""
Middleware para capturar usuario e IP en auditoría
"""
from threading import current_thread


class AuditoriaMiddleware:
    """
    Middleware que almacena el usuario actual y la IP en el thread local
    para que las señales de auditoría puedan acceder a ellos
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread = current_thread()

        # Guardar el request completo en el thread para que las señales
        # puedan acceder al usuario autenticado por DRF después
        thread.auditoria_request = request

        # Obtener IP del cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        thread.auditoria_ip = ip

        response = self.get_response(request)

        # Limpiar el thread
        if hasattr(thread, 'auditoria_request'):
            delattr(thread, 'auditoria_request')
        if hasattr(thread, 'auditoria_ip'):
            delattr(thread, 'auditoria_ip')

        return response
