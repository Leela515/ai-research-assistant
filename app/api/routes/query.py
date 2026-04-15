from fastapi import APIRouter, Depends
from app.schemas.query import QueryRequest, QueryResponse
from app.services.answer_service import AnswerService
from app.core.dependencies import get_answer_service

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    answer_service: AnswerService = Depends(get_answer_service)
):
    return answer_service.answer_question(request.question)