import json
from typing import Optional
import uuid
from app.deps import get_chroma_client
from app.schemas.res import QuestionItem
from config import DUPLICATE_THRESHOLD, SCORE_THRESHOLD


async def search_similar_questions(
    question: QuestionItem, subject: str, topic: str, top_k: int = 3
) -> list[dict]:
    """Search ChromaDB for similar questions"""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=f"{subject.strip().lower()}",
            metadata={"hnsw:space": "cosine"},
        )

        # Search for similar questions
        results = collection.query(
            query_texts=[question.question],
            n_results=top_k,
            include=["documents", "distances"],
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
                        else {},
                    }
                )

        return similar_questions
    except Exception as e:
        print(f"Error searching similar questions: {e}")
        return []


async def add_question_to_chroma(
    question: QuestionItem,
    subject: str,
    topic: str,
    score: float,
    validation_issues: list[str],
    duplication_chance: float,
) -> tuple[bool, Optional[str]]:
    try:
        if duplication_chance > DUPLICATE_THRESHOLD or score < SCORE_THRESHOLD :
            print(f"Question not added to ChromaDB due to low score ({score}) or high duplication chance ({duplication_chance})")
            return False, None

        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=f"{subject.strip().lower()}",
            metadata={"hnsw:space": "cosine"},
        )

        # Add to collection
        uuid_str = uuid.uuid4().hex
        collection.add(
            documents=[question.question],
            metadatas=[
                {
                    "correct_option": question.correct_option.value,
                    "explanation": question.explanation,
                    "issues": json.dumps(validation_issues),
                    "subject": subject,
                    "topic": topic,
                    "options": json.dumps(question.options.model_dump()),
                }
            ],
            ids=[uuid_str],
        )

        print(
            f"Question added to ChromaDB with score {score} and duplication chance {duplication_chance}"
        )
        return True, uuid_str
    except Exception as e:
        print(f"Error adding question to ChromaDB: {e}")
        return False, None
