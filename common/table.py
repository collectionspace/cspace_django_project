from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.contrib.auth.models import User

# thanks http://ericsaupe.com/reportlab-and-django-part-2-headers-and-footers-with-page-numbers/

class makeReport:
    def __init__(self, buffer, pagesize, headertext, footertext):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
        self.headertext = headertext
        self.footertext = footertext


    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph('', styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        # Footer
        footer = Paragraph('', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()


    def fillReport(self, data):
            buffer = self.buffer
            doc = SimpleDocTemplate(buffer,
                                    rightMargin=72,
                                    leftMargin=72,
                                    topMargin=72,
                                    bottomMargin=72,
                                    headertext=self.headertext,
                                    footertext=self.footertext,
                                    pagesize=self.pagesize)

            # Our container for 'Flowable' objects
            elements = []

            # A large collection of style sheets pre-made for us
            styles = getSampleStyleSheet()
            #styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

            #Configure style and word wrap
            s = getSampleStyleSheet()
            s = s["BodyText"]
            s.wordWrap = 'CJK'
            #format the data table
            data2 = [[Paragraph(cell, s) for cell in row] for row in data]
            t=Table(data2, repeatRows=1)
            #Send the data and build the file
            elements.append(Paragraph('Report', styles['Heading2']))
            elements.append(t)

            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)

            # Get the value of the BytesIO buffer and write it to the response.
            pdf = buffer.getvalue()
            buffer.close()
            return pdf
