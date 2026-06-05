import logging

import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


async def save_uploaded_image(file: UploadFile, db: Session, db_image_model) -> int:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        logger.info("Upload started for file: %s", file.filename)
        result = cloudinary.uploader.upload(file.file)
        cloud_image = db_image_model(
            url=result["secure_url"],
            public_id=result["public_id"],
        )
        db.add(cloud_image)
        db.flush()
        logger.info("Upload successful: %s (id=%s)", result["public_id"], cloud_image.id)
        return cloud_image.id
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Upload error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc
