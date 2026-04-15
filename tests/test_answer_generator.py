from core.answer_generator import AnswerGenerator


def test_answer_pipeline_runs():
    ag = AnswerGenerator()
    result = ag.answer("What is ANN-SNN conversion?")

    assert isinstance(result, str)
    assert "Sources:" in result