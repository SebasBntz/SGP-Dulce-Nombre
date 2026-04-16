from fpdf import FPDF
from app.models.all_models import ActaBautizo, ActaMatrimonio, ActaConfirmacion, ActaComunion
from datetime import datetime

class PDFService:
    def _safe_str(self, text):
        if text is None: return ""
        if not isinstance(text, str): text = str(text)
        # Convert to latin-1 and handle special characters
        try:
            return text.encode('latin-1', 'replace').decode('latin-1')
        except:
            return ""

    def _header(self, pdf, title_doc=None):
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 5, self._safe_str("DIOCESIS DE MAGANGUE"), ln=1, align='C')
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 6, self._safe_str("PARROQUIA DULCE NOMBRE DE JESUS"), ln=1, align='C')
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 5, self._safe_str("JUAN ARIAS, BOLIVAR - COLOMBIA"), ln=1, align='C')
        pdf.ln(5)
        if title_doc:
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 7, self._safe_str(title_doc), ln=1, align='C')
            pdf.ln(5)

    def _footer(self, pdf):
        pdf.set_y(-30)
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(0, 4, self._safe_str("Calle 21 Carrera #16-9 Barrio Centro. Celular: 320 754 9852 - Juan Arias, Bolivar - Colombia"), ln=1, align='C')
        pdf.set_font("helvetica", "U", 8)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 4, self._safe_str("parroquiadulcenombredejesus@outlook.es"), ln=1, align='C')
        pdf.set_text_color(0, 0, 0)

    def _format_date_long(self, dt):
        if not dt: return ""
        try:
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d")
            
            months = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            return f"{dt.day} DE {months[dt.month - 1]} DE {dt.year}"
        except:
            return self._safe_str(str(dt))

    def generate_matrimonio_pdf(self, acta: ActaMatrimonio) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        # Original Title style
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 5, self._safe_str("DIOCESIS DE MAGANGUE"), ln=1, align='C')
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 6, self._safe_str("PARROQUIA DULCE NOMBRE DE JESUS"), ln=1, align='C')
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 5, self._safe_str("JUAN ARIAS, BOLIVAR - COLOMBIA"), ln=1, align='C')
        pdf.ln(5)

        # Title on its own line
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, self._safe_str("PARTIDA DE MATRIMONIO"), ln=1, align='L')
        
        # Book info on separate lines to guarantee visibility
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Libro.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.libro), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Folio.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.folio), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Numero......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.numero), ln=1)
        pdf.ln(4)

        def add_line(label, value, dots=35):
            pdf.set_font("helvetica", "B", 10)
            label_fixed = (label + "." * max(0, dots - len(label)) + ":")
            pdf.cell(65, 7, self._safe_str(label_fixed), ln=0)
            pdf.set_font("helvetica", "", 10)
            text_val = self._safe_str(value).upper()
            pdf.cell(0, 7, f" {text_val}", ln=1)

        add_line("FECHA DE MATRIMONIO", self._format_date_long(acta.fecha_matrimonio))
        add_line("EL ESPOSO", f"{acta.nombre_esposo or ''} {acta.apellidos_esposo or ''}")
        add_line("HIJO DE", acta.padres_esposo)
        add_line("BAUTIZADO", acta.parroquia_bautizo_esposo)
        add_line("EL DIA", self._format_date_long(acta.fecha_bautizo_esposo))
        
        add_line("LA ESPOSA", f"{acta.nombre_esposa or ''} {acta.apellidos_esposa or ''}")
        add_line("BAUTIZADA", acta.parroquia_bautizo_esposa)
        add_line("EL DIA", self._format_date_long(acta.fecha_bautizo_esposa))
        add_line("HIJA DE", acta.padres_esposa)
        
        testigos = acta.testigos if acta.testigos else " Y ".join([t for t in [acta.nombre_testigo1, acta.nombre_testigo2] if t])
        add_line("TESTIGOS", testigos)
        add_line("PRESENCIO", acta.nombre_cura)
        add_line("LEGITIMACION DE HIJOS", acta.legitimacion_hijos)
        add_line("DA FE", acta.da_fe)
        
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("." * 40 + " NOTA AL MARGEN " + "." * 40), ln=1, align='C')
        pdf.set_font("helvetica", "", 9)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        pdf.multi_cell(0, 5, self._safe_str(nota_text).upper(), align='L')
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("PBRO. DANUIL SANTOS MANJARREZ GONZALEZ"), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')

        self._footer(pdf)
        return bytes(pdf.output())

    def generate_bautizo_pdf(self, acta: ActaBautizo) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 5, self._safe_str("DIOCESIS DE MAGANGUE"), ln=1, align='C')
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 6, self._safe_str("PARROQUIA DULCE NOMBRE DE JESUS"), ln=1, align='C')
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 5, self._safe_str("JUAN ARIAS, BOLIVAR - COLOMBIA"), ln=1, align='C')
        pdf.ln(5)

        # Title and Book info
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, self._safe_str("PARTIDA DE BAUTISMO"), ln=1, align='L')
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Libro.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.libro), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Folio.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.folio), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(25, 6, self._safe_str("Numero......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(acta.numero), ln=1)
        pdf.ln(4)

        def add_line(label, value, dots=35):
            pdf.set_font("helvetica", "B", 10)
            label_fixed = (label + "." * max(0, dots - len(label)) + ":")
            pdf.cell(65, 7, self._safe_str(label_fixed), ln=0)
            pdf.set_font("helvetica", "", 10)
            text_val = self._safe_str(value).upper() if value else ""
            pdf.cell(0, 7, f" {text_val}", ln=1)

        add_line("APELLIDOS", acta.apellidos)
        add_line("NOMBRES", acta.nombre)
        add_line("FECHA DE NACIMIENTO", self._format_date_long(acta.fecha_nacimiento))
        add_line("LUGAR DE NACIMIENTO", acta.lugar_nacimiento)
        add_line("FECHA DE BAUTIZO", self._format_date_long(acta.fecha_bautizo))
        add_line("NOMBRE PADRE", acta.nombre_padre)
        add_line("NOMBRE MADRE", acta.nombre_madre)
        
        abuelos_paternos = acta.abuelos_paternos if acta.abuelos_paternos else f"{acta.nombre_abuelo_paterno or ''} - {acta.nombre_abuela_paterna or ''}"
        add_line("ABUELOS PATERNOS", abuelos_paternos)
        
        abuelos_maternos = acta.abuelos_maternos if acta.abuelos_maternos else f"{acta.nombre_abuelo_materno or ''} - {acta.nombre_abuela_materna or ''}"
        add_line("ABUELOS MATERNOS", abuelos_maternos)
        
        padrinos = f"{acta.nombre_padrino or ''} - {acta.nombre_madrina or ''}" if (acta.nombre_padrino or acta.nombre_madrina) else ""
        add_line("PADRINOS", padrinos)
        add_line("MINISTRO", acta.nombre_cura)
        add_line("DA FE", acta.da_fe)

        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("." * 40 + " NOTA AL MARGEN " + "." * 40), ln=1, align='C')
        pdf.set_font("helvetica", "", 9)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"SIN NOTA MARGINAL DE MATRIMONIO HASTA LA FECHA. LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        pdf.multi_cell(0, 5, self._safe_str(nota_text).upper(), align='L')

        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("PBRO. ALFARO ENRIQUE CASARES HURTADO"), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')

        self._footer(pdf)
        return bytes(pdf.output())

    def _premium_header(self, pdf, title_doc):
        # Draw Logo placeholder or space
        pdf.ln(5)
        # We don't have the image file, so we leave space for a physical stamp or digital logo if added later
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 5, self._safe_str("DIOCESIS DE MAGANGUE"), ln=1, align='C')
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 6, self._safe_str("PARROQUIA DULCE NOMBRE DE JESUS"), ln=1, align='C')
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 5, self._safe_str("JUAN ARIAS, BOLIVAR - COLOMBIA"), ln=1, align='C')
        pdf.ln(5)
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 7, self._safe_str(title_doc), ln=1, align='C')
        pdf.ln(2)

    def _add_book_info_premium(self, pdf, libro, folio, numero):
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 6, self._safe_str("LIBRO.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(libro or ''), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 6, self._safe_str("FOLIO.......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(folio or ''), ln=1)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 6, self._safe_str("NÚMERO......:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, self._safe_str(numero or ''), ln=1)
        pdf.ln(4)

    def _add_field_premium(self, pdf, label, value):
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(60, 7, self._safe_str(f"{label}:"), ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 7, self._safe_str(str(value or '').upper()), ln=1)

    def generate_confirmacion_pdf(self, acta: ActaConfirmacion) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        self._premium_header(pdf, "PARTIDA DE CONFIRMACIÓN")
        self._add_book_info_premium(pdf, acta.libro, acta.folio, acta.numero)

        self._add_field_premium(pdf, "APELLIDOS", acta.apellidos)
        self._add_field_premium(pdf, "NOMBRES", acta.nombre)
        self._add_field_premium(pdf, "FECHA DE CONFIRMACIÓN", self._format_date_long(acta.fecha_confirmacion))
        self._add_field_premium(pdf, "LUGAR", acta.lugar_confirmacion or "JUAN ARIAS - PARROQUIA DULCE NOMBRE DE JESUS")
        self._add_field_premium(pdf, "LUGAR DEL BAUTISMO", acta.lugar_bautismo or acta.parroquia_bautizo)
        self._add_field_premium(pdf, "NOMBRE DEL PADRE", acta.nombre_padre)
        self._add_field_premium(pdf, "NOMBRE DE LA MADRE", acta.nombre_madre)
        self._add_field_premium(pdf, "PADRINO (A)", acta.nombre_padrino)
        self._add_field_premium(pdf, "MINISTRO", acta.obispo or acta.nombre_cura)
        self._add_field_premium(pdf, "DA FE", acta.da_fe)
        
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("NOTA AL MARGEN"), ln=1, align='C')
        pdf.set_font("helvetica", "", 9)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        pdf.multi_cell(0, 5, self._safe_str(nota_text).upper(), align='L')
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str(acta.da_fe or "PBRO. PARROCO"), ln=1, align='C')
        
        self._footer(pdf)
        return bytes(pdf.output())

    def generate_comunion_pdf(self, acta: ActaComunion) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        self._premium_header(pdf, "PARTIDA DE PRIMERA COMUNIÓN")
        self._add_book_info_premium(pdf, acta.libro, acta.folio, acta.numero)

        self._add_field_premium(pdf, "APELLIDOS", acta.apellidos)
        self._add_field_premium(pdf, "NOMBRES", acta.nombre)
        self._add_field_premium(pdf, "FECHA DE COMUNIÓN", self._format_date_long(acta.fecha_comunion))
        self._add_field_premium(pdf, "LUGAR", acta.lugar_comunion or "JUAN ARIAS - PARROQUIA DULCE NOMBRE DE JESUS")
        self._add_field_premium(pdf, "LUGAR DEL BAUTISMO", acta.lugar_bautismo or acta.parroquia_bautizo)
        self._add_field_premium(pdf, "NOMBRE DEL PADRE", acta.nombre_padre)
        self._add_field_premium(pdf, "NOMBRE DE LA MADRE", acta.nombre_madre)
        
        padrinos = []
        if acta.padrino: padrinos.append(acta.padrino)
        if acta.madrina: padrinos.append(acta.madrina)
        self._add_field_premium(pdf, "PADRINO (A)", " Y ".join(padrinos))
        
        self._add_field_premium(pdf, "MINISTRO", acta.nombre_cura)
        self._add_field_premium(pdf, "DA FE", acta.da_fe)
        
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("NOTA AL MARGEN"), ln=1, align='C')
        pdf.set_font("helvetica", "", 9)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        pdf.multi_cell(0, 5, self._safe_str(nota_text).upper(), align='L')
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str(acta.da_fe or "PBRO. PARROCO"), ln=1, align='C')
        
        self._footer(pdf)
        return bytes(pdf.output())

pdf_service = PDFService()
