from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi import status as s
from tauth.schemas import Creator

router = APIRouter()


@router.post("/events", status_code=s.HTTP_201_CREATED)
async def create_event(
    request: Request,
    background_tasks: BackgroundTasks,
    event: dict[str, str],
):
    pass
