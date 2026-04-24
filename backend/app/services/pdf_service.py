import os
from fpdf import FPDF
from app.models.all_models import ActaBautizo, ActaMatrimonio, ActaConfirmacion, ActaComunion
from datetime import datetime

class PDFService:
    def _safe_str(self, text):
        if text is None: return ""
        if not isinstance(text, str): text = str(text)
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

    def _get_telefono_cura(self, firmante_name):
        if not firmante_name:
            return "320 754 9852" # Fallback
        try:
            from app.db.session import SessionLocal
            from app.models.all_models import Sacerdote
            db = SessionLocal()
            sacerdotes = db.query(Sacerdote).all()
            db.close()
            firmante_upper = firmante_name.upper()
            for s in sacerdotes:
                full_name = f"{s.nombres} {s.apellidos}".upper()
                if full_name in firmante_upper or firmante_upper in full_name:
                    return s.telefono if s.telefono else "320 754 9852"
            return "320 754 9852"
        except:
            return "320 754 9852"

    def _footer(self, pdf, firmante_name=""):
        telefono_cura = self._get_telefono_cura(firmante_name)
        
        pdf.set_y(-30)
        pdf.set_font("helvetica", "B", 8)
        
        address_text = "Calle 21 Carrera #16-9 Barrio Centro."
        phone_text = f" Celular: {telefono_cura} -" if telefono_cura else ""
        location_text = " Juan Arias, Bolivar - Colombia"
        
        full_footer = address_text + phone_text + location_text
        pdf.cell(0, 4, self._safe_str(full_footer), ln=1, align='C')
        
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

    def _add_book_info_centered(self, pdf, libro, folio, numero):
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, self._safe_str(f"LIBRO.......: {libro or ''}"), ln=1, align='C')
        pdf.cell(0, 6, self._safe_str(f"FOLIO.......: {folio or ''}"), ln=1, align='C')
        pdf.cell(0, 6, self._safe_str(f"NUMERO......: {numero or ''}"), ln=1, align='C')
        pdf.ln(4)

    def _add_line(self, pdf, label, value):
        pdf.set_font("helvetica", "B", 10)
        target_x = 75
        
        w_label = pdf.get_string_width(label)
        pdf.cell(w_label, 7, self._safe_str(label), ln=0)
        
        current_x = pdf.get_x()
        dots_space = target_x - current_x
        if dots_space > 0:
            dot_w = pdf.get_string_width(".")
            num_dots = int(dots_space / dot_w)
            pdf.cell(dots_space, 7, self._safe_str("." * num_dots), ln=0, align='R')
        
        pdf.cell(3, 7, ":", ln=0)
        
        pdf.set_font("helvetica", "", 10)
        text_val = self._safe_str(value).upper() if value else ""
        pdf.cell(0, 7, f" {text_val}", ln=1)

    def _print_marginal_note(self, pdf, nota_text):
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("." * 40 + " NOTA AL MARGEN " + "." * 40), ln=1, align='C')
        pdf.set_font("helvetica", "", 9)
        
        text = self._safe_str(nota_text).upper()
        pdf.write(5, text)
        
        # Fill the rest of the line with dots
        current_x = pdf.get_x()
        target_x = pdf.w - pdf.r_margin
        if current_x < target_x:
            dot_w = pdf.get_string_width(".")
            num_dots = int((target_x - current_x) / dot_w)
            pdf.write(5, "." * num_dots)
        pdf.ln(5)

    def generate_bautizo_pdf(self, acta: ActaBautizo) -> bytes:
        pdf = FPDF()
        pdf.set_margins(15, 30, 15)
        pdf.add_page()
        
        self._header(pdf, "PARTIDA DE BAUTISMO")
        self._add_book_info_centered(pdf, acta.libro, acta.folio, acta.numero)

        self._add_line(pdf, "APELLIDOS", acta.apellidos)
        self._add_line(pdf, "NOMBRES", acta.nombre)
        self._add_line(pdf, "FECHA DE NACIMIENTO", self._format_date_long(acta.fecha_nacimiento))
        self._add_line(pdf, "LUGAR DE NACIMIENTO", acta.lugar_nacimiento)
        self._add_line(pdf, "FECHA DE BAUTIZO", self._format_date_long(acta.fecha_bautizo))
        self._add_line(pdf, "NOMBRE PADRE", acta.nombre_padre)
        self._add_line(pdf, "NOMBRE MADRE", acta.nombre_madre)
        
        abuelos_paternos = acta.abuelos_paternos if acta.abuelos_paternos else f"{acta.nombre_abuelo_paterno or ''} - {acta.nombre_abuela_paterna or ''}"
        self._add_line(pdf, "ABUELOS PATERNOS", abuelos_paternos.strip(" -"))
        
        abuelos_maternos = acta.abuelos_maternos if acta.abuelos_maternos else f"{acta.nombre_abuelo_materno or ''} - {acta.nombre_abuela_materna or ''}"
        self._add_line(pdf, "ABUELOS MATERNOS", abuelos_maternos.strip(" -"))
        
        padrinos = f"{acta.nombre_padrino or ''} - {acta.nombre_madrina or ''}" if (acta.nombre_padrino or acta.nombre_madrina) else ""
        self._add_line(pdf, "PADRINOS", padrinos.strip(" -"))
        self._add_line(pdf, "MINISTRO", acta.nombre_cura)
        self._add_line(pdf, "DA FE", acta.da_fe)

        cert_date = self._format_date_long(datetime.now())
        nota_default = f"SIN NOTA MARGINAL DE BAUTISMO HASTA LA FECHA. LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        self._print_marginal_note(pdf, nota_text)

        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        firmante = acta.parroco_firmante or acta.nombre_cura or "PARROCO"
        pdf.cell(0, 5, self._safe_str(firmante.upper()), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')

        self._footer(pdf, firmante)
        return bytes(pdf.output())

    def generate_matrimonio_pdf(self, acta: ActaMatrimonio) -> bytes:
        pdf = FPDF()
        pdf.set_margins(15, 30, 15)
        pdf.add_page()
        
        self._header(pdf, "PARTIDA DE MATRIMONIO")
        self._add_book_info_centered(pdf, acta.libro, acta.folio, acta.numero)

        self._add_line(pdf, "FECHA DE MATRIMONIO", self._format_date_long(acta.fecha_matrimonio))
        self._add_line(pdf, "EL ESPOSO", f"{acta.nombre_esposo or ''} {acta.apellidos_esposo or ''}")
        self._add_line(pdf, "HIJO DE", acta.padres_esposo)
        self._add_line(pdf, "BAUTIZADO EN", acta.parroquia_bautizo_esposo)
        self._add_line(pdf, "EL DIA", self._format_date_long(acta.fecha_bautizo_esposo))
        
        self._add_line(pdf, "LA ESPOSA", f"{acta.nombre_esposa or ''} {acta.apellidos_esposa or ''}")
        self._add_line(pdf, "HIJA DE", acta.padres_esposa)
        self._add_line(pdf, "BAUTIZADA EN", acta.parroquia_bautizo_esposa)
        self._add_line(pdf, "EL DIA", self._format_date_long(acta.fecha_bautizo_esposa))
        
        testigos = acta.testigos if acta.testigos else " Y ".join([t for t in [acta.nombre_testigo1, acta.nombre_testigo2] if t])
        self._add_line(pdf, "TESTIGOS", testigos)
        self._add_line(pdf, "PRESENCIO", acta.nombre_cura)
        self._add_line(pdf, "LEGITIMACION HIJOS", acta.legitimacion_hijos)
        self._add_line(pdf, "DA FE", acta.da_fe)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"SIN NOTA MARGINAL DE MATRIMONIO HASTA LA FECHA. LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        self._print_marginal_note(pdf, nota_text)
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        firmante = acta.parroco_firmante or acta.nombre_cura or "PARROCO"
        pdf.cell(0, 5, self._safe_str(firmante.upper()), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')

        self._footer(pdf, firmante)
        return bytes(pdf.output())

    def generate_confirmacion_pdf(self, acta: ActaConfirmacion) -> bytes:
        pdf = FPDF()
        pdf.set_margins(15, 30, 15)
        pdf.add_page()
        
        self._header(pdf, "PARTIDA DE CONFIRMACIÓN")
        self._add_book_info_centered(pdf, acta.libro, acta.folio, acta.numero)

        self._add_line(pdf, "APELLIDOS", acta.apellidos)
        self._add_line(pdf, "NOMBRES", acta.nombre)
        self._add_line(pdf, "FECHA CONFIRMACION", self._format_date_long(acta.fecha_confirmacion))
        self._add_line(pdf, "LUGAR", acta.lugar_confirmacion or "JUAN ARIAS - PARROQUIA DULCE NOMBRE DE JESUS")
        self._add_line(pdf, "LUGAR DEL BAUTISMO", acta.lugar_bautismo or acta.parroquia_bautizo)
        self._add_line(pdf, "NOMBRE DEL PADRE", acta.nombre_padre)
        self._add_line(pdf, "NOMBRE DE LA MADRE", acta.nombre_madre)
        
        padrinos = []
        if acta.nombre_padrino: padrinos.append(acta.nombre_padrino)
        if acta.nombre_madrina: padrinos.append(acta.nombre_madrina)
        self._add_line(pdf, "PADRINO (A)", " Y ".join(padrinos))
        
        self._add_line(pdf, "MINISTRO", acta.nombre_cura)
        self._add_line(pdf, "OBISPO", acta.obispo)
        self._add_line(pdf, "DA FE", acta.da_fe)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"SIN NOTA MARGINAL DE CONFIRMACIÓN HASTA LA FECHA. LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        self._print_marginal_note(pdf, nota_text)
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        firmante = acta.parroco_firmante or acta.da_fe or acta.nombre_cura or "PARROCO"
        pdf.cell(0, 5, self._safe_str(firmante.upper()), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')
        
        self._footer(pdf, firmante)
        return bytes(pdf.output())

    def generate_comunion_pdf(self, acta: ActaComunion) -> bytes:
        pdf = FPDF()
        pdf.set_margins(15, 30, 15)
        pdf.add_page()
        
        self._header(pdf, "PARTIDA DE PRIMERA COMUNIÓN")
        self._add_book_info_centered(pdf, acta.libro, acta.folio, acta.numero)

        self._add_line(pdf, "APELLIDOS", acta.apellidos)
        self._add_line(pdf, "NOMBRES", acta.nombre)
        self._add_line(pdf, "FECHA DE COMUNION", self._format_date_long(acta.fecha_comunion))
        self._add_line(pdf, "LUGAR", acta.lugar_comunion or "JUAN ARIAS - PARROQUIA DULCE NOMBRE DE JESUS")
        self._add_line(pdf, "LUGAR DEL BAUTISMO", acta.lugar_bautismo or acta.parroquia_bautizo)
        self._add_line(pdf, "NOMBRE DEL PADRE", acta.nombre_padre)
        self._add_line(pdf, "NOMBRE DE LA MADRE", acta.nombre_madre)
        
        padrinos = []
        if acta.padrino: padrinos.append(acta.padrino)
        if acta.madrina: padrinos.append(acta.madrina)
        self._add_line(pdf, "PADRINO (A)", " Y ".join(padrinos))
        
        self._add_line(pdf, "MINISTRO", acta.nombre_cura)
        self._add_line(pdf, "DA FE", acta.da_fe)
        
        cert_date = self._format_date_long(datetime.now())
        nota_default = f"SIN NOTA MARGINAL DE PRIMERA COMUNIÓN HASTA LA FECHA. LA INFORMACIÓN SUMINISTRADA ES FIEL A LA CONTENIDA EN EL LIBRO. SE EXPIDE EN JUAN ARIAS, BOLÍVAR - COLOMBIA EL DÍA {cert_date}."
        nota_text = acta.nota_al_margen if acta.nota_al_margen else nota_default
        self._print_marginal_note(pdf, nota_text)
        
        pdf.ln(20)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 5, self._safe_str("__________________________"), ln=1, align='C')
        firmante = acta.parroco_firmante or acta.da_fe or acta.nombre_cura or "PARROCO"
        pdf.cell(0, 5, self._safe_str(firmante.upper()), ln=1, align='C')
        pdf.cell(0, 5, self._safe_str("PARROCO"), ln=1, align='C')
        
        self._footer(pdf, firmante)
        return bytes(pdf.output())

pdf_service = PDFService()
