import os
from fastapi import UploadFile
from pathlib import Path
from typing import Optional
from uuid import uuid4
from app.config import settings


async def save_audio_file(file: UploadFile, user_id: int) -> Optional[str]:
    try:
        # Create user directory if not exists
        user_dir = Path(f"app/storage/user_{user_id}")
        user_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid4()}.{file_ext}"
        file_path = user_dir / filename

        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return str(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return None