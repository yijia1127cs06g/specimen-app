import datetime
import json
import logging
from typing import Dict

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from db.models import create_specimen_identifier
from specimen.schemas import SpecimenCreate


SINICA_SPECIMEN_FIELD_MAPPING = {
    '中文種名': 'species_name',
    '學名': 'scientific_name',
    '標本館號': 'collection_number',
    '編目號': 'catalog_number',
    '引用': 'reference',
    '採集日期': 'collection_date',
    '採集者': 'collector',
    '緯度': 'latitude',
    '經度': 'longitude',
    '國家': 'country',
    '行政區': 'area',
    '最低海拔': 'minimum_altitude',
}

DEFAULT_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

SINICA_BASE_URL = 'https://sinica.digitalarchives.tw'


async def fetch_image_from_sinica(url):
    async with aiohttp.request(
        'GET',
        url,
        headers=DEFAULT_HEADERS,
        timeout=5,
    ) as response:
        image = await response.read()
        return image


async def fetch_specimen_list_from_sinica(session: ClientSession, page: int = 1):
    async with session.post(
        url=f'{SINICA_BASE_URL}/_partial/_collection_list.php',
        data={
            'page': page,
            'type': 3799,
        },
        headers=DEFAULT_HEADERS | {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://sinica.digitalarchives.tw',
            'referer': f'https://sinica.digitalarchives.tw/collection.php?type=3799&page={page}',
        },
        timeout=7,
    ) as response:
        response_text = await response.text()
        try:
            data = json.loads(response_text)
        except Exception as e:
            logging.warning(f'[fetch_specimen_list] parsing json data occurs error: {e},'
                            f' response content: {response_text[:500]}')
            return {}
        return data


async def fetch_specimen_html_from_sinica(session: ClientSession, specimen_website_id):
    async with session.get(
        url=f'{SINICA_BASE_URL}/collection_{specimen_website_id}.html',
        headers=DEFAULT_HEADERS,
        timeout=7,
    ) as response:
        response_html = await response.text()
        return response_html


def parse_specimen_from_sinica(html_text) -> Dict:
    soup = BeautifulSoup(html_text, 'html.parser')
    specimen = SpecimenCreate()

    # parse generally
    for dd in soup.find_all('dd'):
        raw_text = dd.get_text()
        for parse_field_name, db_field_name in SINICA_SPECIMEN_FIELD_MAPPING.items():
            if parse_field_name in raw_text:
                db_value = raw_text.split(':')[1].strip()
                if db_field_name == 'collection_date':
                    db_value = datetime.datetime.strptime(db_value, '%Y-%m-%d').date()
                setattr(specimen, db_field_name, db_value)
                break

    # parse reference
    quote = soup.find('div', class_='set quote')
    if quote:
        quote_textarea = quote.find('textarea')
        if quote_textarea:
            specimen.reference = quote_textarea.get_text().split('https://sinica.digitalarchives.tw/collection_')[0]

    # parse image_url
    meta_image = soup.find('meta', property='og:image')
    if meta_image:
        specimen.image_url = meta_image['content']

    meta_url = soup.find('meta', property='og:url')
    specimen_sinica_id = meta_url['content'].split('/')[-1].replace('collection_', '').replace('.html', '')

    specimen.identifier = create_specimen_identifier(
        external_identifier=specimen_sinica_id,
        website='sinica'
    )

    return specimen.model_dump()


SINICA_SPECIMEN_V2_FIELD_MAPPING = {
    '植物標本館館號': 'collection_number',
    '採集者': 'collector',
    '標本採集地': 'area',
}


def parse_specimen_from_sinica_v2(html_text) -> Dict:
    soup = BeautifulSoup(html_text, 'html.parser')
    specimen = SpecimenCreate()

    # parse parse generally
    for dd in soup.find_all('dd'):
        raw_text = dd.get_text()
        raw_text = raw_text.replace('：', ':')

        # handle collection_date specially
        try:
            db_value = datetime.datetime.strptime(raw_text, '%Y-%m-%d').date()
            setattr(specimen, 'collection_date', db_value)
        except:
            pass

        for parse_field_name, db_field_name in SINICA_SPECIMEN_V2_FIELD_MAPPING.items():
            if parse_field_name in raw_text:
                db_value = raw_text.split(':')[1].strip()
                setattr(specimen, db_field_name, db_value)
                break
            elif '經緯度' in raw_text:
                lat, long = raw_text.split(':')[1].strip().split(' ')[:2]
                setattr(specimen, 'latitude', lat)
                setattr(specimen, 'longitude', long)
            elif '海拔:' in raw_text:
                raw_text = raw_text.replace('海拔:', '')
                minimum_altitude = raw_text.split('-')[0]
                setattr(specimen, 'minimum_altitude', minimum_altitude)

    quote = soup.find('div', class_='set quote')
    if quote:
        quote_textarea = quote.find('textarea')
        if quote_textarea:
            specimen.reference = quote_textarea.get_text().split('https://sinica.digitalarchives.tw/collection_')[0]

    # parse image_url
    meta_image = soup.find('meta', property='og:image')
    if meta_image:
        specimen.image_url = meta_image['content']

    # parse species_name
    specimen.species_name = soup.find('h1', id='collection-title').get_text()

    meta_url = soup.find('meta', property='og:url')
    specimen_sinica_id = meta_url['content'].split('/')[-1].replace('collection_', '').replace('.html', '')

    specimen.identifier = create_specimen_identifier(
        external_identifier=specimen_sinica_id,
        website='sinica'
    )

    return specimen.model_dump()
