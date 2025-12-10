from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from app.schemas.mongo_models import (
    GenerationLog,
    ComprehensionLog,
    FillInTheBlankLog,
    SubjectiveLog,
)

router = APIRouter()


@router.get("/question")
async def get_question_log(session_id: str):
    """Get MCQ generation log by session ID"""
    try:
        object_id = PydanticObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    log = await GenerationLog.find_one({"_id": object_id})
    
    if not log:
        raise HTTPException(status_code=404, detail="Question log not found")
    
    return {
        **log.model_dump(),
        "id": str(log.id) if hasattr(log, "id") else None,
        "created_at": log.created_at.isoformat() if hasattr(log, "created_at") and log.created_at else None,
    }


@router.get("/comprehension")
async def get_comprehension_log(session_id: str):
    """Get comprehension generation log by session ID"""
    try:
        object_id = PydanticObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    log = await ComprehensionLog.find_one({"_id": object_id})
    
    if not log:
        raise HTTPException(status_code=404, detail="Comprehension log not found")
    
    return {
        **log.model_dump(),
        "id": str(log.id) if hasattr(log, "id") else None,
        "created_at": log.created_at.isoformat() if hasattr(log, "created_at") and log.created_at else None,
    }


@router.get("/fill-in-the-blank")
async def get_fill_in_the_blank_log(session_id: str):
    """Get fill-in-the-blank generation log by session ID"""
    try:
        object_id = PydanticObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    log = await FillInTheBlankLog.find_one({"_id": object_id})
    
    if not log:
        raise HTTPException(status_code=404, detail="Fill-in-the-blank log not found")
    
    return {
        **log.model_dump(),
        "id": str(log.id) if hasattr(log, "id") else None,
        "created_at": log.created_at.isoformat() if hasattr(log, "created_at") and log.created_at else None,
    }


@router.get("/subjective")
async def get_subjective_log(session_id: str):
    """Get subjective generation log by session ID"""
    try:
        object_id = PydanticObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    log = await SubjectiveLog.find_one({"_id": object_id})
    
    if not log:
        raise HTTPException(status_code=404, detail="Subjective log not found")
    
    return {
        **log.model_dump(),
        "id": str(log.id) if hasattr(log, "id") else None,
        "created_at": log.created_at.isoformat() if hasattr(log, "created_at") and log.created_at else None,
    }
