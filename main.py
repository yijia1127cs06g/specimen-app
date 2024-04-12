import logging
from http import HTTPStatus

from fastapi import FastAPI
from contextlib import asynccontextmanager

from db.main import init_db
from specimen.routes import specimen_router
from reportlab.pdfbase import pdfmetrics, ttfonts


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("server starting")
    pdfmetrics.registerFont(ttfonts.TTFont('openhuninn', 'jf-openhuninn-1.1.ttf'))
    await init_db()
    yield
    logging.info("server is shutting down")

description = """
simple specimen app.

## Specimen

You will be able to:

* **Get specimens**
* **Get specimen**
* **Get specimen pdf**
"""


app = FastAPI(
    title='Specimen App',
    version='0.1.0',
    description=description,
    lifespan=lifespan,
)


@app.get('/', status_code=HTTPStatus.OK)
async def index():
    return {'message': 'Hi~ This is Specimen App for specimen'}

app.include_router(specimen_router, tags=['Specimen'])
