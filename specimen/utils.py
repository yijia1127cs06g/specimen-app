import io
import logging
from typing import Dict

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from db.models import FIELD_DESCRIPTION_MAPPING
from specimen.crawl_utils import fetch_image_from_sinica


PDF_FIELD_SEQUENCE = [
    'species_name', 'scientific_name', 'collection_number', 'catalog_number', 'collection_date', 'collector',
    'latitude', 'longitude', 'country', 'area', 'minimum_altitude', 'reference',
]


async def create_specimen_pdf(specimen_data: Dict, buffer: io.BytesIO | None = None) -> io.BytesIO:
    """
    Create a PDF document for specimen data.

    Params:
        specimen_data (Dict): Dictionary containing specimen data, where keys are field names and values are field values.

        buffer: BytesIO object to store the PDF data. If not provided, a new BytesIO object will be created.

    Returns:
        Buffer: BytesIO object containing the PDF data.
    """
    if buffer is None:
        buffer = io.BytesIO()

    page = canvas.Canvas(buffer)
    page.setFont(psfontname='openhuninn', size=12)

    image_url = specimen_data.pop('image_url', '')

    y = 700
    image_buffer = io.BytesIO()
    if image_url:
        try:
            image_bytes = await fetch_image_from_sinica(image_url)
            image_buffer.write(image_bytes)
            image_buffer.seek(0)
            image = ImageReader(image_buffer)
        except Exception as e:
            logging.warning(f'[get_specimen_pdf] handling image occurs error: {e}')
        else:
            page.drawImage(image, (page._pagesize[0] - 200) / 2, y - 150, width=200, height=200)
            y -= 200

    for field in PDF_FIELD_SEQUENCE:
        value = specimen_data.get(field, '')
        field_name = FIELD_DESCRIPTION_MAPPING.get(field)
        if field_name:
            page.drawString(100, y, f'{field_name}: {value}'.encode('utf-8'))
            y -= 20

    page.showPage()
    page.save()

    image_buffer.close()
    buffer.seek(0)

    return buffer
