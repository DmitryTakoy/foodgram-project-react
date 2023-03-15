
import os
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate
from rest_framework.decorators import api_view
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Image as PDFImage
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Frame
from reportlab.platypus import PageTemplate
from reportlab.platypus import BaseDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph


from .models import (
    Recipe,
    IngredientAmount,
    ShoppingList
)
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
@api_view(['POST', 'GET'])
@csrf_exempt
def download_shopping_cart_t(request):
    print("download_shopping_cart function was called")
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    user = request.user
    favorite_rec = ShoppingList.objects.filter(user=user)
    recipes = Recipe.objects.filter(shopping_lists__in=favorite_rec)
    ingredients = IngredientAmount.objects.select_related('ingredient').filter(recipe__in=recipes)

    shopping_cart = {}
    for ingredient in ingredients:
        name = ingredient.ingredient.name
        if name in shopping_cart:
            shopping_cart[name]['amount'] += ingredient.amount
        else:
            shopping_cart[name] = {
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }

    buffer = BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Arial'
    styles['Normal'].fontSize = 20
    styles['Normal'].textColor = HexColor("#000000")
    styles['Normal'].leading = 52 # Adjust the value as needed

    frame_margin_left = 1.2 * inch
    frame_margin_top = 2 * inch
    frame_width = 10 * inch
    frame_height = 9 * inch

    class BackgroundPageTemplate(PageTemplate):
        def beforeDrawPage(self, canvas, doc):
            draw_background_image(canvas, doc)
    
    def draw_background_image(canvas, doc):
        canvas.saveState()
        file_name = 'layer.jpg'
        img_path = os.path.join(settings.MEDIA_ROOT, file_name)
        im = Image.open(img_path)
        im = im.resize(tuple(map(int, A4)), Image.ANTIALIAS)
        pdf_img = ImageReader(im)
        canvas.drawImage(pdf_img, 0, 0, A4[0], A4[1])
        canvas.restoreState()

    frame = Frame(frame_margin_left, A4[1] - frame_margin_top - frame_height, frame_width, frame_height)
    doc.addPageTemplates([BackgroundPageTemplate(frames=frame)])

    square = "<font name='Arial' size=35>☐</font>"
    ingredients_text = "<br/>".join(f"{name}: {data['amount']} {data['measurement_unit']} {square}" for name, data in shopping_cart.items())
    ingredients_p = Paragraph(ingredients_text, styles["Normal"])

    story = [ingredients_p]

    doc.build(story)

    buffer.seek(0)

    file_name = f"{user.username}_shopping_cart.pdf"
    file_content = buffer.getvalue()
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, 'wb') as f:
        f.write(file_content)

    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response