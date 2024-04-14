import asyncio
import json
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.models import Specimen


async def save_specimens(async_db_session, specimens):
    async with async_db_session() as session:
        async with session.begin():

            session.add_all([Specimen.model_validate(specimen) for specimen in specimens])


async def main():
    async_engine = create_async_engine(url=f'sqlite+aiosqlite:///{os.environ["DB_FILENAME"]}', echo=False)

    async_db_session = async_sessionmaker(async_engine, expire_on_commit=False)

    fixture_list = os.listdir('fixtures')
    for fixture in fixture_list:
        with open(f'fixtures/{fixture}') as f:
            specimens = json.load(f)

        await save_specimens(async_db_session, specimens)


if __name__ == '__main__':
    asyncio.run(main())
