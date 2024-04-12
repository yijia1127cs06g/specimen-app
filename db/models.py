import datetime

from sqlmodel import SQLModel, Field


class SpecimenBase(SQLModel):

    scientific_name: str = Field(default='', description='學名', )
    species_name: str = Field(default='', description='中文種名')
    collection_number: str = Field(default='', description='標本館號')
    catalog_number: str = Field(default='', description='編目號')
    reference: str = Field(default='', description='引用')
    collection_date: datetime.date | None = Field(default=None, nullable=True, description='採集日期')
    collector: str = Field(default='', description='採集者')
    latitude: float | None = Field(default=None, nullable=True, description='緯度')
    longitude: float | None = Field(default=None, nullable=True, description='經度')
    country: str = Field(default='', description='國家')
    area: str = Field(default='', description='行政區')
    minimum_altitude: float | None = Field(default=None, nullable=True, description='最低海拔')
    image_url: str = Field(default='')

    def __repr__(self) -> str:
        return f'Specimen => {self.species_name}'


class Specimen(SpecimenBase, table=True):

    __tablename__ = 'specimens'

    id: int | None = Field(default=None, primary_key=True)
    identifier: str = Field(unique=True)


def create_specimen_identifier(external_identifier: str | int, website: str = '') -> str:
    return f'{website}-{external_identifier}'


FIELD_DESCRIPTION_MAPPING = {
    field_name: field.description for field_name, field in SpecimenBase.__fields__.items()
}
