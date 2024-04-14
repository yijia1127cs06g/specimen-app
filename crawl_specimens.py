import logging
import os

import aiohttp
import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import Specimen
from specimen.crawl_utils import fetch_specimen_html_from_sinica, parse_specimen_from_sinica, \
    parse_specimen_from_sinica_v2

async_engine = create_async_engine(url=f'sqlite+aiosqlite:///{os.environ["DB_FILENAME"]}', echo=False)


TEST_MODE = False


async def select_and_update_specimen(async_session: async_sessionmaker[AsyncSession], specimen_data) -> None:
    async with async_session() as session:
        async with session.begin():

            statement = select(Specimen).where(
                Specimen.identifier == specimen_data['identifier']
            ).limit(1)

            result = await session.execute(statement)

            specimen = result.scalars().one()

            for field, value in specimen_data.items():
                setattr(specimen, field, value)
            await session.commit()


async def get_uncrawl_specimens_identifier(async_db_session, limit):
    async with async_db_session() as session:
        async with session.begin():
            statement = select(Specimen).filter(Specimen.species_name == '').limit(limit)
            result = await session.execute(statement)
            return [specimen.identifier for specimen in result.scalars()]


async def crawl_specimens(specimen_sinica_id_split):

    async_db_session = async_sessionmaker(async_engine, expire_on_commit=False)

    async with aiohttp.ClientSession() as session:
        for specimen_sinica_id in specimen_sinica_id_split:
            try:
                if not TEST_MODE:
                    specimen_html = await fetch_specimen_html_from_sinica(session, specimen_sinica_id)
                else:
                    with open(f'example_html/{specimen_sinica_id}.html') as f:
                        specimen_html = f.read()

                # Try different parse function, since the format of specimen html is varied
                parse_success = False
                for parse_function in [parse_specimen_from_sinica, parse_specimen_from_sinica_v2]:
                    try:
                        specimen = parse_function(specimen_html)
                    except:
                        logging.warning(f'Failed to parse specimen: {specimen_sinica_id},'
                                        f' using parse_function: {parse_function}')
                        continue
                    else:
                        parse_success = True
                        break

                if parse_success:
                    await select_and_update_specimen(async_db_session, specimen)

            except Exception as e:
                logging.warning(f'[crawl_specimens] crawl specimen {specimen_sinica_id} occurs error: {e}')
                continue
            if not TEST_MODE:
                await asyncio.sleep(1)


def split_range(range_, split):
    k, m = divmod(len(range_), split)
    return (range_[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(split))


async def main(limit, concurrency=3):

    async_db_session = async_sessionmaker(async_engine, expire_on_commit=False)

    # Get unfinished specimens from db
    uncrawl_specimen_identifiers = await get_uncrawl_specimens_identifier(async_db_session, limit)

    specimen_sinica_ids = [
        uncrawl_specimen_identifier.split('-')[-1] for uncrawl_specimen_identifier in uncrawl_specimen_identifiers
    ]

    # Split the crawled sinica ids evenly
    specimen_sinica_id_splits = split_range(specimen_sinica_ids, concurrency)

    tasks = []

    for specimen_sinica_id_split in specimen_sinica_id_splits:
        task = asyncio.create_task(crawl_specimens(specimen_sinica_id_split))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl the unfinished specimen')
    parser.add_argument('--limit', type=int, default=100, help='Limit of specimen to crawl')
    parser.add_argument('--concurrency', type=int, default=3, help='Concurrency')
    parser.add_argument('--test-mode', type=bool, default=False, help='Enable test mode')
    args = parser.parse_args()

    TEST_MODE = args.test_mode

    asyncio.run(main(args.limit, args.concurrency))
