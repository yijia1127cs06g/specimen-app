from http import HTTPStatus
import io
from typing import List, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from db.main import get_db_async_session
from specimen.dal import SpecimenDal
from specimen.schemas import SpecimenPublic
from specimen.utils import create_specimen_pdf

specimen_router = APIRouter(prefix='/specimens')


@specimen_router.get('/', status_code=HTTPStatus.OK, response_model=List[SpecimenPublic])
async def get_specimens(
    session: AsyncSession = Depends(get_db_async_session),
    offset: int = 0,
    limit: int = Query(default=20, le=100)
) -> Any:
    specimens = await SpecimenDal(session).all(offset=offset, limit=limit)

    return specimens


@specimen_router.get(r'/{specimen_id}/download/', status_code=HTTPStatus.OK)
async def get_specimen_pdf(
    specimen_id: int | str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_async_session),
) -> Response:

    buffer = io.BytesIO()

    specimen = await SpecimenDal(session).get(int(specimen_id))
    specimen_data = specimen.model_dump(exclude={'id', 'identifier'})

    await create_specimen_pdf(specimen_data, buffer)

    background_tasks.add_task(buffer.close)
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(buffer.getvalue(), headers=headers, media_type='application/pdf')


@specimen_router.get('/{specimen_id}/', status_code=HTTPStatus.OK, response_model=SpecimenPublic)
async def get_specimen(
    specimen_id: str | int,
    session: AsyncSession = Depends(get_db_async_session),
) -> Any:
    specimen = await SpecimenDal(session).get(int(specimen_id))

    return specimen
