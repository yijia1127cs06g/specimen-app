from db.models import SpecimenBase


class SpecimenCreate(SpecimenBase):
    identifier: str | None = None


class SpecimenPublic(SpecimenBase):
    id: int
