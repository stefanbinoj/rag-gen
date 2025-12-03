from typing import Optional
import uuid
from app.deps import get_chroma_client
from app.schemas.output_schema import QuestionItem
from config import DUPLICATE_THRESHOLD, SCORE_THRESHOLD


async def search_similar_questions(
    question: str, subject: str,topic: str, top_k: int = 3
) -> list[dict]:
    """Search ChromaDB for similar questions"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=f"{subject.strip().lower()}.{topic.strip().lower()}",
            metadata={"hnsw:space": "cosine"},
        )

        # Search for similar questions
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            include=["documents", "distances", "metadatas"],
        )

        similar_questions = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                similar_questions.append(
                    {
                        "question": doc,
                        "distance": results["distances"][0][i]
                        if results["distances"]
                        else None,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else None,
                    }
                )

        return similar_questions
    except Exception as e:
        print(f"Error searching similar questions: {e}")
        return []


async def add_question_to_chroma(
    question: str,
    subject: str,
    topic: str,
    score: float,
    duplication_chance: float,
) -> tuple[bool, Optional[str]]:
    try:
        if duplication_chance > DUPLICATE_THRESHOLD or score < SCORE_THRESHOLD:
            return False, None

        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=f"{subject.strip().lower()}.{topic.strip().lower()}",
            metadata={"hnsw:space": "cosine"},
        )

        # Add to collection
        uuid_str = uuid.uuid4().hex
        collection.add(
            documents=[question],
            metadatas=[
                {
                    "subject": subject,
                    "topic": topic,
                }
            ],
            ids=[uuid_str],
        )

        return True, uuid_str
    except Exception as e:
        print(f"Error adding question to ChromaDB: {e}")
        return False, None
