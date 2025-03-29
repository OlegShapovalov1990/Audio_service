from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.auth import get_password_hash
from typing import List


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserCreate):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    for var, value in vars(user_update).items():
        if value is not None:
            if var == "password":
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, var, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    await db.delete(db_user)
    await db.commit()
    return db_user


async def get_audios(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Audio)
        .filter(models.Audio.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_user_audio(db: AsyncSession, audio: schemas.AudioCreate, user_id: int, path: str):
    db_audio = models.Audio(**audio.dict(), owner_id=user_id, path=path)
    db.add(db_audio)
    await db.commit()
    await db.refresh(db_audio)
    return db_audio