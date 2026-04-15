from app.services.answer_service import AnswerService

def get_answer_service() -> AnswerService:
    return AnswerService()