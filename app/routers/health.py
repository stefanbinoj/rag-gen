from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/status")
async def status():
    return JSONResponse(content={"status": "ok"}, status_code=200)


