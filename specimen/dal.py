from sqlmodel.ext.asyncio.session import AsyncSession
from db.models import Specimen
from specimen.schemas import SpecimenCreate
from sqlmodel import select


class SpecimenDal:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, specimen_id: int):
        """
        Get a specimen by its id.

        Params:
            specimen_id (str): the id of the specimen.

        Returns:
            specimen: the specimen object.
        """
        statement = select(Specimen).where(Specimen.id == specimen_id)

        result = await self.session.exec(statement)

        return result.first()

    async def create(self, specimen: SpecimenCreate):
        """
        Create a new specimen.

        Params:
            specimen (SpecimenCreate): data to create a new specimen.

        Returns:
            Specimen: the specimen object.
        """
        new_specimen = Specimen(**specimen.model_dump())

        self.session.add(new_specimen)

        await self.session.commit()

        return new_specimen

    async def all(self):
        """
        Get the list of all specimens.

        Returns:
            list: list of specimen object.
        """
        statement = select(Specimen).order_by(Specimen.id)

        result = await self.session.exec(statement)

        return result.all()
