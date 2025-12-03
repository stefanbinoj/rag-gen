from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.mongo_models import (
    ComprehensionLog,
    FillInTheBlankLog,
    GenerationLog,
    SubjectiveLog,
)

router = APIRouter()


@router.get("/")
async def get_history(offset: int = 0, limit: int = 10):
    try:
        # Get total count
        total_count = await GenerationLog.count()

        logs = (
            await GenerationLog.find()
            .sort("created_at", "-1")
            .skip(offset)
            .limit(limit)
            .to_list()
        )

        return JSONResponse(
            content={
                "status": "ok",
                "data": [
                    {
                        **log.model_dump(),
                        "id": str(log.id) if hasattr(log, "id") else None,
                        "created_at": log.created_at.isoformat()
                        if hasattr(log, "created_at") and log.created_at
                        else None,
                    }
                    for log in logs
                ],
                "total": total_count,
                "count": len(logs),
                "limit": limit,
                "offset": offset,
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comprehension")
async def get_comprehension_history(offset: int = 0, limit: int = 10):
    try:
        total_count = await ComprehensionLog.count()

        logs = (
            await ComprehensionLog.find()
            .sort("created_at", "-1")
            .skip(offset)
            .limit(limit)
            .to_list()
        )

        return JSONResponse(
            content={
                "status": "ok",
                "data": [
                    {
                        **log.model_dump(),
                        "id": str(log.id) if hasattr(log, "id") else None,
                        "created_at": log.created_at.isoformat()
                        if hasattr(log, "created_at") and log.created_at
                        else None,
                    }
                    for log in logs
                ],
                "total": total_count,
                "count": len(logs),
                "limit": limit,
                "offset": offset,
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fill-in-the-blank")
async def get_fill_in_the_blank_history(offset: int = 0, limit: int = 10):
    try:
        total_count = await FillInTheBlankLog.count()

        logs = (
            await ComprehensionLog.find()
            .sort("created_at", "-1")
            .skip(offset)
            .limit(limit)
            .to_list()
        )

        return JSONResponse(
            content={
                "status": "ok",
                "data": [
                    {
                        **log.model_dump(),
                        "id": str(log.id) if hasattr(log, "id") else None,
                        "created_at": log.created_at.isoformat()
                        if hasattr(log, "created_at") and log.created_at
                        else None,
                    }
                    for log in logs
                ],
                "total": total_count,
                "count": len(logs),
                "limit": limit,
                "offset": offset,
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subjective")
async def get_subjective_history(offset: int = 0, limit: int = 10):
    try:
        total_count = await SubjectiveLog.count()

        logs = (
            await ComprehensionLog.find()
            .sort("created_at", "-1")
            .skip(offset)
            .limit(limit)
            .to_list()
        )

        return JSONResponse(
            content={
                "status": "ok",
                "data": [
                    {
                        **log.model_dump(),
                        "id": str(log.id) if hasattr(log, "id") else None,
                        "created_at": log.created_at.isoformat()
                        if hasattr(log, "created_at") and log.created_at
                        else None,
                    }
                    for log in logs
                ],
                "total": total_count,
                "count": len(logs),
                "limit": limit,
                "offset": offset,
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
