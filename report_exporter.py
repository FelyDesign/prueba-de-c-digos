import sys
import reportlab
import io
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    Spacer,
    Image,
    TableStyle,
)
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os


class EnhancedReportExporter:
    def __init__(self, analysis_results, report_data):
        self.results = analysis_results
        self.report = report_data
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
        self.summary_data = self._initialize_summary_data()

    def _initialize_summary_data(self):
        """Inicializa la estructura de datos del resumen"""
        return {
            "critical_issues": 0,
            "moderate_issues": 0,
            "minor_issues": 0,
            "priority_improvements": [],
            "total_issues": 0,
            "overall_status": "No analizado",
        }

    def _create_custom_styles(self):
        """Crea estilos personalizados para el PDF"""
        return {
            "Title": ParagraphStyle(
                "CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,
            ),
            "Subtitle": ParagraphStyle(
                "CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=18,
                spaceAfter=20,
                alignment=1,
            ),
            "Heading2": ParagraphStyle(
                "CustomHeading2",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=24,
            ),
            "Heading3": ParagraphStyle(
                "CustomHeading3",
                parent=self.styles["Heading3"],
                fontSize=14,
                spaceAfter=10,
                spaceBefore=20,
            ),
            "Normal": ParagraphStyle(
                "CustomNormal", parent=self.styles["Normal"], fontSize=12, spaceAfter=12
            ),
            "List": ParagraphStyle(
                "CustomList",
                parent=self.styles["Normal"],
                fontSize=12,
                leftIndent=20,
                spaceAfter=10,
            ),
        }

    def _analyze_issues(self):
        """Analiza los problemas del sitio y actualiza summary_data"""
        if not isinstance(self.results, dict):
            self.summary_data = self._initialize_summary_data()
            return

        self.summary_data = self._initialize_summary_data()

        # Analizar problemas técnicos
        tech_seo = self.results.get("technical_seo", {})
        if tech_seo:
            html_structure = tech_seo.get("html_structure", {})
            if html_structure and not html_structure.get("has_doctype", False):
                self.summary_data["moderate_issues"] += 1
                self.summary_data["priority_improvements"].append(
                    {"issue": "Falta declaración DOCTYPE", "priority": "media"}
                )

        # Analizar meta datos
        meta_data = self.results.get("meta_data", {})
        if meta_data:
            title_tag = meta_data.get("title_tag", {})
            if title_tag and title_tag.get("optimal_length") == "bad":
                self.summary_data["critical_issues"] += 1
                self.summary_data["priority_improvements"].append(
                    {"issue": "Título no optimizado", "priority": "alta"}
                )

            img_alt = meta_data.get("img_alt", {})
            if img_alt and img_alt.get("without_alt", 0) > 0:
                self.summary_data["minor_issues"] += 1
                self.summary_data["priority_improvements"].append(
                    {"issue": "Imágenes sin texto alternativo", "priority": "baja"}
                )

        # Analizar mobile
        mobile = self.results.get("mobile", {})
        if mobile:
            responsive = mobile.get("responsive_design", {})
            if responsive and not responsive.get("has_fluid_images", False):
                self.summary_data["critical_issues"] += 1
                self.summary_data["priority_improvements"].append(
                    {"issue": "Diseño no responsive", "priority": "alta"}
                )

        self._update_summary_status()

    def _update_summary_status(self):
        """Actualiza el estado general del resumen"""
        self.summary_data["total_issues"] = (
            self.summary_data["critical_issues"]
            + self.summary_data["moderate_issues"]
            + self.summary_data["minor_issues"]
        )

        self.summary_data["overall_status"] = (
            "Necesita mejoras críticas"
            if self.summary_data["critical_issues"] > 0
            else (
                "Necesita mejoras"
                if self.summary_data["moderate_issues"] > 0
                else "Buen estado"
            )
        )

    def _check_system_status(self):
        """Verifica el estado del sistema y los permisos"""

    status = {
        "reports_dir": "/home/Felipeeee/reports",
        "dir_exists": False,
        "dir_writable": False,
        "python_version": sys.version,
        "reportlab_version": reportlab.__version__,
        "user": os.getenv("USER"),
        "current_dir": os.getcwd(),
    }

    try:
        os.makedirs(status["reports_dir"], exist_ok=True)
        status["dir_exists"] = os.path.exists(status["reports_dir"])
        status["dir_writable"] = os.access(status["reports_dir"], os.W_OK)
    except Exception as e:
        status["error"] = str(e)

    return status

    def export_pdf(self, filename=None):
        """Exporta el reporte mejorado a PDF"""

    try:
        # Asegurar que el directorio existe
        reports_dir = "/home/Felipeeee/reports"
        try:
            os.makedirs(reports_dir, exist_ok=True)
            print(f"Directorio creado/verificado: {reports_dir}")
        except Exception as dir_error:
            print(f"Error al crear directorio: {str(dir_error)}")
            reports_dir = "/tmp"  # Directorio alternativo
            print(f"Usando directorio alternativo: {reports_dir}")

        if filename is None:
            filename = os.path.join(
                reports_dir,
                f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            )

        print(f"Generando PDF en: {filename}")

        # Verificar que self.results existe
        if not self.results:
            raise Exception("No hay resultados para generar el reporte")

        # Analizar issues
        self._analyze_issues()
        print("Análisis completado")

        # Crear el PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        print("Iniciando generación de contenido")

        # Agregar secciones con verificación
        try:
            story.extend(self._create_cover_page())
            story.append(Spacer(1, 30))
            print("Portada creada")

            story.append(
                Paragraph("Plan Básico - Análisis SEO", self.custom_styles["Subtitle"])
            )
            story.append(Spacer(1, 30))

            story.extend(self._create_executive_summary())
            story.append(Spacer(1, 20))
            print("Resumen ejecutivo creado")

            story.extend(self._create_detailed_metrics())
            story.append(Spacer(1, 20))
            print("Métricas detalladas creadas")

            story.extend(self._create_strengths_section())
            story.append(Spacer(1, 20))
            print("Sección de fortalezas creada")

            story.extend(self._create_detailed_action_plan())
            story.append(Spacer(1, 20))
            print("Plan de acción creado")

            story.extend(self._create_next_steps())
            print("Próximos pasos creados")

        except Exception as section_error:
            print(f"Error al crear sección: {str(section_error)}")
            raise

        # Construir el PDF
        print("Iniciando construcción del PDF")
        try:
            doc.build(story)
            print("PDF construido exitosamente")
        except Exception as build_error:
            print(f"Error al construir PDF: {str(build_error)}")
            raise

        # Verificar que el archivo se creó
        if not os.path.exists(filename):
            raise Exception("El archivo PDF no se generó correctamente")

        print(f"PDF generado exitosamente en: {filename}")
        return filename

    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        print(f"Detalles adicionales: {getattr(e, '__dict__', {})}")
        raise Exception(f"Error al generar PDF: {str(e)}")

    def _create_cover_page(self):
        """Crea la portada del reporte"""
        elements = []
        elements.append(
            Paragraph("Reporte de Análisis SEO", self.custom_styles["Title"])
        )
        elements.append(Spacer(1, 30))

        url = self.results.get("url", "No disponible")
        elements.append(
            Paragraph(f"URL Analizada: {url}", self.custom_styles["Subtitle"])
        )
        elements.append(
            Paragraph(
                f"Fecha de Análisis: {datetime.now().strftime('%d/%m/%Y')}",
                self.custom_styles["Normal"],
            )
        )
        return elements

    def _create_executive_summary(self):
        """Crea el resumen ejecutivo"""
        elements = []
        elements.append(Paragraph("Resumen Ejecutivo", self.custom_styles["Heading2"]))

        if not hasattr(self, "summary_data") or not self.summary_data:
            self._analyze_issues()

        data = [
            ["Métrica", "Valor"],
            ["Estado General", self.summary_data.get("overall_status", "No analizado")],
            ["Problemas Críticos", str(self.summary_data.get("critical_issues", 0))],
            ["Problemas Moderados", str(self.summary_data.get("moderate_issues", 0))],
            ["Problemas Menores", str(self.summary_data.get("minor_issues", 0))],
            ["Total de Problemas", str(self.summary_data.get("total_issues", 0))],
        ]

        table = Table(data, colWidths=[200, 300])
        table.setStyle(self._get_table_style())
        elements.append(table)
        return elements

    def _get_table_style(self):
        """Retorna el estilo básico para tablas"""
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )

    def _create_detailed_metrics(self):
        """Crea sección detallada de métricas"""
        elements = []
        elements.append(
            Paragraph("Análisis Detallado de Métricas", self.custom_styles["Heading2"])
        )

        # 1. Análisis Técnico SEO
        elements.append(
            Paragraph("1. Análisis Técnico SEO", self.custom_styles["Heading3"])
        )
        tech_data = [
            ["Métrica", "Estado", "Detalles"],
            [
                "Estructura HTML",
                (
                    "OK"
                    if self.results.get("technical_seo", {})
                    .get("html_structure", {})
                    .get("has_html_tag")
                    else "Necesita Mejoras"
                ),
                self._get_html_structure_details(),
            ],
            [
                "SSL/HTTPS",
                (
                    "OK"
                    if self.results.get("technical_seo", {})
                    .get("ssl_check", {})
                    .get("has_ssl")
                    else "Necesita Mejoras"
                ),
                self._get_ssl_details(),
            ],
            [
                "Robots.txt",
                (
                    "OK"
                    if self.results.get("technical_seo", {})
                    .get("robots_txt", {})
                    .get("exists")
                    else "Necesita Mejoras"
                ),
                self._get_robots_details(),
            ],
            [
                "Sitemap",
                (
                    "OK"
                    if self.results.get("technical_seo", {})
                    .get("sitemap", {})
                    .get("exists")
                    else "Necesita Mejoras"
                ),
                self._get_sitemap_details(),
            ],
        ]
        elements.append(
            Table(tech_data, colWidths=[150, 100, 250], style=self._get_table_style())
        )
        elements.append(Spacer(1, 15))

        # 2. Meta Datos
        elements.append(Paragraph("2. Meta Datos", self.custom_styles["Heading3"]))
        meta = self.results.get("meta_data", {})
        meta_data = [
            ["Elemento", "Estado", "Contenido/Detalles"],
            [
                "Title Tag",
                (
                    "OK"
                    if meta.get("title_tag", {}).get("optimal_length") == "good"
                    else "Necesita Mejoras"
                ),
                f"Actual: {meta.get('title_tag', {}).get('content', 'No disponible')} ({meta.get('title_tag', {}).get('length', 0)} caracteres)",
            ],
            [
                "Meta Description",
                (
                    "OK"
                    if meta.get("meta_description", {}).get("optimal_length") == "good"
                    else "Necesita Mejoras"
                ),
                f"Longitud: {meta.get('meta_description', {}).get('length', 0)} caracteres",
            ],
            [
                "Headers",
                (
                    "OK"
                    if meta.get("headers", {}).get("h1", {}).get("count") == 1
                    else "Necesita Mejoras"
                ),
                self._get_headers_details(),
            ],
            [
                "Alt Text",
                (
                    "OK"
                    if meta.get("img_alt", {}).get("without_alt", 1) == 0
                    else "Necesita Mejoras"
                ),
                f"{meta.get('img_alt', {}).get('with_alt', 0)} imágenes con alt, {meta.get('img_alt', {}).get('without_alt', 0)} sin alt",
            ],
        ]
        elements.append(
            Table(meta_data, colWidths=[150, 100, 250], style=self._get_table_style())
        )
        elements.append(Spacer(1, 15))

        # 3. Performance
        elements.append(Paragraph("3. Performance", self.custom_styles["Heading3"]))
        perf = self.results.get("performance", {})
        perf_data = [
            ["Métrica", "Valor", "Estado"],
            [
                "Tiempo de Carga",
                f"{perf.get('load_time', {}).get('time_seconds', 0)} segundos",
                perf.get("load_time", {}).get("rating", "N/A"),
            ],
            [
                "Tamaño de Página",
                f"{perf.get('page_size', {}).get('size_mb', 0)} MB",
                perf.get("page_size", {}).get("rating", "N/A"),
            ],
            [
                "Status Code",
                str(perf.get("status_code", {}).get("code", 0)),
                "OK" if perf.get("status_code", {}).get("code") == 200 else "Revisar",
            ],
        ]
        elements.append(
            Table(perf_data, colWidths=[150, 150, 100], style=self._get_table_style())
        )
        elements.append(Spacer(1, 15))

        # 4. Mobile
        elements.append(Paragraph("4. Mobile", self.custom_styles["Heading3"]))
        mobile = self.results.get("mobile", {})
        mobile_data = [
            ["Elemento", "Estado", "Detalles"],
            [
                "Viewport",
                (
                    "OK"
                    if mobile.get("viewport", {}).get("is_responsive")
                    else "Necesita Mejoras"
                ),
                self._get_viewport_details(),
            ],
            [
                "Responsive Design",
                (
                    "OK"
                    if mobile.get("responsive_design", {}).get("has_fluid_images")
                    else "Necesita Mejoras"
                ),
                self._get_responsive_details(),
            ],
        ]
        elements.append(
            Table(mobile_data, colWidths=[150, 100, 250], style=self._get_table_style())
        )
        return elements

    def _get_html_structure_details(self):
        """Obtiene detalles de la estructura HTML"""
        structure = self.results.get("technical_seo", {}).get("html_structure", {})
        return f"{'Tiene' if structure.get('has_doctype') else 'Falta'} DOCTYPE, {'Tiene' if structure.get('has_head') else 'Falta'} HEAD"

    def _get_ssl_details(self):
        """Obtiene detalles del SSL"""
        ssl = self.results.get("technical_seo", {}).get("ssl_check", {})
        return f"Certificado {'válido' if ssl.get('has_ssl') else 'no encontrado'}"

    def _get_robots_details(self):
        """Obtiene detalles del robots.txt"""
        robots = self.results.get("technical_seo", {}).get("robots_txt", {})
        return (
            f"{'Archivo presente' if robots.get('exists') else 'Archivo no encontrado'}"
        )

    def _get_sitemap_details(self):
        """Obtiene detalles del sitemap"""
        sitemap = self.results.get("technical_seo", {}).get("sitemap")
        if sitemap is None:
            return "No encontrado"
        if isinstance(sitemap, dict) and sitemap.get("exists"):
            return f"Presente con {sitemap.get('url_count', 0)} URLs"
        return "No encontrado"

    def _get_current_state(self, issue):
        """Obtiene el estado actual del problema"""
        if not isinstance(issue, dict) or "issue" not in issue:
            return "Estado no especificado"

        if not isinstance(self.results, dict):
            return "No hay datos disponibles"

        meta_data = self.results.get("meta_data", {})
        tech_seo = self.results.get("technical_seo", {})
        mobile = self.results.get("mobile", {})

        states = {
            "Título no optimizado": lambda: f"Título actual tiene {meta_data.get('title_tag', {}).get('length', 0)} caracteres",
            "Diseño no responsive": lambda: "Faltan elementos responsive en la página",
            "Falta declaración DOCTYPE": lambda: "Página sin declaración DOCTYPE",
            "Imágenes sin texto alternativo": lambda: f"{meta_data.get('img_alt', {}).get('without_alt', 0)} imágenes sin alt text",
        }

        state_func = states.get(issue.get("issue"))
        if state_func:
            try:
                return state_func()
            except Exception:
                return "Estado no disponible"
        return "Estado no especificado"

    def _get_headers_details(self):
        """Obtiene detalles de los headers"""
        headers = self.results.get("meta_data", {}).get("headers", {})
        h1_count = headers.get("h1", {}).get("count", 0)
        h2_count = headers.get("h2", {}).get("count", 0)
        h3_count = headers.get("h3", {}).get("count", 0)
        return f"H1: {h1_count}, H2: {h2_count}, H3: {h3_count}"

    def _get_viewport_details(self):
        """Obtiene detalles del viewport"""
        viewport = self.results.get("mobile", {}).get("viewport", {})
        if viewport and viewport.get("is_responsive"):
            return "Configurado correctamente"
        return "Necesita configuración"

    def _get_responsive_details(self):
        """Obtiene detalles del diseño responsive"""
        responsive = self.results.get("mobile", {}).get("responsive_design", {})
        if responsive and responsive.get("has_media_queries"):
            return "Diseño responsive implementado"
        return "Falta implementación responsive"

    def _get_technical_solution(self, issue):
        """Obtiene la solución técnica para un problema"""
        if not isinstance(issue, dict) or "issue" not in issue:
            return "Solución no especificada"

        solutions = {
            "Título no optimizado": "Ajustar el título a una longitud entre 30-60 caracteres",
            "Diseño no responsive": "Implementar media queries y hacer las imágenes fluidas",
            "Falta declaración DOCTYPE": "Agregar <!DOCTYPE html> al inicio del documento",
            "Imágenes sin texto alternativo": "Agregar atributos alt descriptivos a las imágenes",
            "Meta descripción no optimizada": "Ajustar la meta descripción a una longitud entre 120-155 caracteres",
        }
        return solutions.get(issue["issue"], "Solución no especificada")

    def _get_implementation_steps(self, issue):
        """Obtiene los pasos de implementación según el problema"""
        if not isinstance(issue, dict) or "issue" not in issue:
            return ["Implementación no especificada"]

        steps = {
            "Título no optimizado": [
                "Revisar el título actual",
                "Incluir palabras clave principales",
                "Ajustar longitud entre 30-60 caracteres",
                "Verificar relevancia para la página",
            ],
            "Diseño no responsive": [
                "Implementar meta viewport",
                "Agregar media queries",
                "Hacer las imágenes fluidas",
                "Probar en diferentes dispositivos",
            ],
            "Falta declaración DOCTYPE": [
                "Agregar <!DOCTYPE html> al inicio del documento",
                "Verificar la estructura HTML",
                "Validar el código HTML",
            ],
            "Imágenes sin texto alternativo": [
                "Identificar imágenes sin alt",
                "Agregar descripciones relevantes",
                "Verificar la accesibilidad",
            ],
            "Meta descripción no optimizada": [
                "Revisar la meta descripción actual",
                "Incluir llamada a la acción clara",
                "Ajustar longitud entre 120-155 caracteres",
                "Verificar relevancia y atractivo",
            ],
        }
        return steps.get(issue["issue"], ["Implementación no especificada"])

    def _get_expected_benefit(self, issue):
        """Obtiene el beneficio esperado de la implementación"""
        if not isinstance(issue, dict) or "issue" not in issue:
            return "Beneficio no especificado"

        benefits = {
            "Título no optimizado": "Mejor posicionamiento en búsquedas y mayor CTR",
            "Diseño no responsive": "Mejor experiencia en móviles y mejor ranking mobile",
            "Falta declaración DOCTYPE": "Mejor renderizado y compatibilidad cross-browser",
            "Imágenes sin texto alternativo": "Mejor accesibilidad y SEO para imágenes",
            "Meta descripción no optimizada": "Mayor visibilidad en resultados de búsqueda y CTR mejorado",
        }
        return benefits.get(issue["issue"], "Beneficio no especificado")

    def _create_strengths_section(self):
        """Crea la sección de fortalezas"""
        elements = []
        elements.append(
            Paragraph("Fortalezas del Sitio", self.custom_styles["Heading2"])
        )

        strengths = self._identify_strengths()
        if strengths:
            for strength in strengths:
                elements.append(Paragraph(f"• {strength}", self.custom_styles["List"]))
        else:
            elements.append(
                Paragraph(
                    "No se identificaron fortalezas significativas en esta evaluación.",
                    self.custom_styles["Normal"],
                )
            )

        return elements

    def _identify_strengths(self):
        """Identifica las fortalezas del sitio"""
        strengths = []

        if not self.results:
            return strengths

        # Verificar rendimiento
        perf = self.results.get("performance", {})
        load_time = perf.get("load_time", {})
        if load_time and load_time.get("rating") == "good":
            strengths.append(
                f"Excelente tiempo de carga: {load_time.get('time_seconds')} segundos"
            )

        page_size = perf.get("page_size", {})
        if page_size and page_size.get("rating") == "good":
            strengths.append(
                f"Tamaño de página optimizado: {page_size.get('size_mb')}MB"
            )

        # Verificar SSL
        tech_seo = self.results.get("technical_seo", {})
        ssl_check = tech_seo.get("ssl_check", {})
        if ssl_check and ssl_check.get("has_ssl"):
            strengths.append("Certificado SSL correctamente implementado")

        # Verificar meta datos
        meta = self.results.get("meta_data", {})
        meta_desc = meta.get("meta_description", {})
        if meta_desc and meta_desc.get("optimal_length") == "good":
            strengths.append("Meta descripción bien optimizada")

        # Verificar imágenes
        img_alt = meta.get("img_alt", {})
        if img_alt and img_alt.get("with_alt", 0) > 0:
            strengths.append(
                f"{img_alt.get('with_alt')} imágenes correctamente etiquetadas"
            )

        return strengths

    def _create_detailed_action_plan(self):
        """Crea plan de acción detallado"""
        elements = []
        elements.append(
            Paragraph("Plan de Acción Detallado", self.custom_styles["Heading2"])
        )

        if not hasattr(self, "summary_data") or not self.summary_data:
            self._analyze_issues()

        priority_improvements = self.summary_data.get("priority_improvements", [])

        if not priority_improvements:
            elements.append(
                Paragraph(
                    "No se identificaron problemas que requieran acciones inmediatas.",
                    self.custom_styles["Normal"],
                )
            )
            return elements

        for issue in priority_improvements:
            if not isinstance(issue, dict):
                continue

            issue_title = issue.get("issue", "Problema no especificado")
            priority = issue.get("priority", "no especificada")

            elements.append(
                Paragraph(
                    f"{issue_title} (Prioridad: {priority})",
                    self.custom_styles["Heading3"],
                )
            )

            current_state = self._get_current_state(issue)
            if current_state:
                elements.append(
                    Paragraph("• Estado Actual:", self.custom_styles["List"])
                )
                elements.append(
                    Paragraph(f"  {current_state}", self.custom_styles["Normal"])
                )

            solution = self._get_technical_solution(issue)
            if solution:
                elements.append(
                    Paragraph("• Solución Recomendada:", self.custom_styles["List"])
                )
                elements.append(
                    Paragraph(f"  {solution}", self.custom_styles["Normal"])
                )

            steps = self._get_implementation_steps(issue)
            if steps:
                elements.append(
                    Paragraph("• Pasos para Implementar:", self.custom_styles["List"])
                )
                for step in steps:
                    elements.append(
                        Paragraph(f"  - {step}", self.custom_styles["Normal"])
                    )

            benefit = self._get_expected_benefit(issue)
            if benefit:
                elements.append(
                    Paragraph("• Beneficio Esperado:", self.custom_styles["List"])
                )
                elements.append(Paragraph(f"  {benefit}", self.custom_styles["Normal"]))

            elements.append(Spacer(1, 10))

        return elements

    def _create_next_steps(self):
        """Crea la sección de próximos pasos"""
        elements = []
        elements.append(
            Paragraph("Próximos Pasos Recomendados", self.custom_styles["Heading2"])
        )

        if not hasattr(self, "summary_data") or not self.summary_data:
            self._analyze_issues()

        priority_improvements = self.summary_data.get("priority_improvements", [])

        if not priority_improvements:
            elements.append(
                Paragraph(
                    "No hay acciones prioritarias pendientes en este momento.",
                    self.custom_styles["Normal"],
                )
            )
            return elements

        quick_wins = [
            issue
            for issue in priority_improvements
            if isinstance(issue, dict) and issue.get("priority") == "alta"
        ]
        if quick_wins:
            elements.append(
                Paragraph(
                    "Acciones Inmediatas (Quick Wins):", self.custom_styles["Heading3"]
                )
            )
            for win in quick_wins:
                elements.append(
                    Paragraph(
                        f"• {win.get('issue', 'No especificado')}",
                        self.custom_styles["List"],
                    )
                )

        medium_priority = [
            issue
            for issue in priority_improvements
            if isinstance(issue, dict) and issue.get("priority") == "media"
        ]
        if medium_priority:
            elements.append(
                Paragraph("Plan a Mediano Plazo:", self.custom_styles["Heading3"])
            )
            for issue in medium_priority:
                elements.append(
                    Paragraph(
                        f"• {issue.get('issue', 'No especificado')}",
                        self.custom_styles["List"],
                    )
                )

        return elements
