from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.services.creations_service import CreationsService
from app.dependencies.auth import get_current_user
from app.dependencies.db_connection import get_db_connection
import asyncpg
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/creations", tags=["creations"])

@router.post("/upload")
async def upload_creation(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: CreationsService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Handles the upload of a media file and its prompt,
    saves it, and returns the new creation's data.
    """
    try:
        user_id = int(current_user["sub"])
        new_creation = await service.save_creation(conn, user_id, prompt, file)
        return new_creation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload creation: {str(e)}")


@router.get("/feed", response_model=List[Dict[str, Any]])
async def get_feed(
    service: CreationsService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Returns a list of all creations for the public feed.
    """
    return await service.get_feed_creations(conn)

@router.delete("/{creation_id}", response_model=Optional[Dict[str, Any]])
async def delete_creation(
    creation_id: int,
    current_user: dict = Depends(get_current_user),
    service: CreationsService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Deletes a creation by its ID, ensuring the user is the owner.
    """
    user_id = int(current_user["sub"])
    deleted_creation = await service.delete_creation(conn, creation_id, user_id)
    return deleted_creation
