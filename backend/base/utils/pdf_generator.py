"""
Utilidades para generar PDFs con WeasyPrint
Sistema modular y reutilizable para todos los reportes
"""
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os


class PDFGenerator:
    """
    Generador de PDFs centralizado
    Uso:
        pdf_gen = PDFGenerator('mi_template.html', context_data, orientation='portrait')
        pdf_bytes = pdf_gen.generate()
    """

    def __init__(self, template_name, context, orientation='portrait', include_header=True):
        """
        Args:
            template_name: Nombre del template HTML
            context: Diccionario con datos para el template
            orientation: 'portrait' o 'landscape'
            include_header: Si incluir la cabecera común con logo
        """
        self.template_name = template_name
        self.context = context
        self.orientation = orientation
        self.include_header = include_header
        self.font_config = FontConfiguration()

    def get_base_context(self):
        """Obtiene contexto base con opciones generales del sistema"""
        from base.models import OpcionGeneral

        opciones = {}
        for opcion in OpcionGeneral.objects.all():
            opciones[opcion.clave] = opcion.valor

        # Path del logo (ajustar según la ubicación real)
        logo_path = self.get_static_path('logo.png') if os.path.exists(
            self.get_static_path('logo.png')) else ''

        return {
            'opciones': opciones,
            'logo_path': logo_path,
            'orientation': self.orientation,
            'include_header': self.include_header,
        }

    def get_full_context(self):
        """Combina contexto base con el contexto proporcionado"""
        full_context = self.get_base_context()
        full_context.update(self.context)
        return full_context

    def get_css(self):
        """Retorna CSS personalizado según orientación"""
        base_css = """
        @page {
            size: A4 %(orientation)s;
            margin: 1cm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 10pt;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header img {
            max-height: 60px;
        }
        .header h1 {
            margin: 5px 0;
            font-size: 16pt;
        }
        table {
            width: 100%%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        table th, table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .text-right {
            text-align: right;
        }
        .text-center {
            text-align: center;
        }
        .totales {
            font-weight: bold;
            background-color: #f9f9f9;
        }
        .no-border {
            border: none;
        }
        """ % {'orientation': self.orientation}

        return CSS(string=base_css, font_config=self.font_config)

    def generate(self):
        """
        Genera el PDF y retorna los bytes
        Returns:
            bytes: Contenido del PDF
        """
        context = self.get_full_context()
        html_string = render_to_string(self.template_name, context)

        html = HTML(string=html_string)
        css = self.get_css()

        pdf_bytes = html.write_pdf(
            stylesheets=[css], font_config=self.font_config)

        return pdf_bytes

    @staticmethod
    def get_static_path(filename):
        """Retorna la ruta absoluta de un archivo en static/"""
        return os.path.join(settings.STATIC_ROOT, filename)
