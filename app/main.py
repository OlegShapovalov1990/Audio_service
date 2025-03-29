from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud, models
from app.database import get_db, engine, Base
from app.auth import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    router as auth_router
)
from app.storage import save_audio_file
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/users/", response_model=schemas.User)
async def create_user(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/", response_model=List[schemas.User])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_superuser)
):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_superuser)
):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
        user_id: int,
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_superuser)
):
    db_user = await crud.update_user(db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_superuser)
):
    db_user = await crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@app.post("/audios/", response_model=schemas.Audio)
async def upload_audio(
        title: str,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_user)
):
    # Save file to storage
    file_path = await save_audio_file(file, current_user.id)
    if not file_path:
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Create audio record in DB
    audio = schemas.AudioCreate(title=title)
    db_audio = await crud.create_user_audio(db, audio=audio, user_id=current_user.id, path=file_path)

    return db_audio


@app.get("/audios/", response_model=List[schemas.Audio])
async def get_audios(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_user)
):
    audios = await crud.get_audios(db, user_id=current_user.id, skip=skip, limit=limit)
    return audios