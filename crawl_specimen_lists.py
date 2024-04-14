import json
import logging
import os

import aiohttp
import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.models import Specimen, create_specimen_identifier
from specimen.crawl_utils import fetch_specimen_list_from_sinica, DEFAULT_HEADERS


TEST_MODE = False


async def save_specimens(async_db_session, specimens):
    async with async_db_session() as session:
        async with session.begin():

            # Query existed identifier to avoid unique constraint when insert many
            statement = select(Specimen).filter(
                Specimen.identifier.in_((specimen.get('identifier') for specimen in specimens))
            )
            result = await session.execute(statement)
            existed_specimens = result.scalars()
            existed_identifiers = {
                existed_specimen.identifier for existed_specimen in existed_specimens
            }
            specimens = list(filter(lambda specimen: specimen['identifier'] not in existed_identifiers, specimens))

            session.add_all([Specimen.model_validate(specimen) for specimen in specimens])


async def crawl_specimen_lists(page_range):

    async_engine = create_async_engine(url=f'sqlite+aiosqlite:///{os.environ["DB_FILENAME"]}', echo=False)

    async_db_session = async_sessionmaker(async_engine, expire_on_commit=False)

    async with aiohttp.ClientSession() as session:
        if not TEST_MODE:
            # Need to get Cookie first for get correct list response
            async with session.get(
                    url='https://sinica.digitalarchives.tw/collection.php?type=3799',
                    headers=DEFAULT_HEADERS,
                    timeout=7,
            ) as response:
                session.cookie_jar.update_cookies(response.cookies)

        for page in page_range:
            try:
                if not TEST_MODE:
                    specimen_raw_data_list = await fetch_specimen_list_from_sinica(session, page)
                else:
                    with open(f'example_page/page-{page}.json') as f:
                        specimen_raw_data_list = json.load(f)

                specimen_website_ids = [specimen.get('id') for specimen in specimen_raw_data_list.get('list', [])]

                new_specimens = [
                    {
                        'identifier': create_specimen_identifier(specimen_website_id, 'sinica')
                    } for specimen_website_id in specimen_website_ids
                ]

                await save_specimens(async_db_session, new_specimens)

            except Exception as e:
                logging.warning(f'[crawl_specimen_lists] crawl page {page} occurs error: {e}')

            if not TEST_MODE:
                await asyncio.sleep(1)

    await async_engine.dispose()


def split_range(range_, split):
    k, m = divmod(len(range_), split)
    return (range_[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(split))


async def main(start_page, end_page, concurrency=3):

    # Split the crawled pages evenly
    page_ranges = split_range(range(start_page, end_page+1), concurrency)

    tasks = []
    for page_range in page_ranges:
        task = asyncio.create_task(crawl_specimen_lists(page_range))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the list of specimen sinica id and save to database')
    parser.add_argument('--start-page', type=int, default=1, help='Start page number')
    parser.add_argument('--end-page', type=int, default=100, help='End page number')
    parser.add_argument('--concurrency', type=int, default=3, help='Concurrency')
    parser.add_argument('--test-mode', type=bool, default=False, help='Enable test mode')

    args = parser.parse_args()

    TEST_MODE = args.test_mode

    asyncio.run(main(args.start_page, args.end_page, args.concurrency))
