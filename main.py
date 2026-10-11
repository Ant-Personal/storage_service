
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

app = FastAPI(title="File Upload API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())

    # Keep only the filename, not any client-supplied path
    original_name = Path(
        file.filename or "unnamed"
    ).name

    # Store under a generated name to prevent collisions
    extension = Path(original_name).suffix
    saved_name = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / saved_name

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
                length=1024 * 1024
            )

        size = file_path.stat().st_size

        if size > MAX_FILE_SIZE:
            file_path.unlink()
            raise HTTPException(
                status_code=413,
                detail="File exceeds 100 MB limit"
            )

        return {
            "message": "File uploaded successfully",
            "file_id": file_id,
            "original_filename": original_name,
            "saved_filename": saved_name,
            "size_bytes": size,
            "status": "uploaded"
        }

    except HTTPException:
        raise
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="File upload failed"
        )
    finally:
        file.file.close()
