from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from office_loan_policy_assistant.main import app
from office_loan_policy_assistant.services.rag_service import (
    answer_policy_question,
)


def test_rag_rejects_unanswerable_question():
    """Reject questions unsupported by retrieved policy evidence."""

    mock_db = Mock()
    mock_model = Mock()
    mock_reranker = Mock()

    chunks = [
        {
            "id": 1,
            "source": "office_loan_policy.pdf",
            "page_number": 3,
            "text": "Personal loans are limited to twice gross monthly salary.",
        }
    ]

    with (
        patch(
            "office_loan_policy_assistant.services.rag_service.hybrid_search",
            return_value=chunks,
        ),
        patch(
            "office_loan_policy_assistant.services.rag_service.rerank_chunks",
            return_value=chunks,
        ),
        patch(
            "office_loan_policy_assistant.services.rag_service.check_answerability",
        ) as mock_answerability,
        patch(
            "office_loan_policy_assistant.services.rag_service.generate_policy_answer"
        ) as mock_generate,
    ):
        mock_answerability.return_value.is_answerable = False

        result = answer_policy_question(
            question="What is the employee laptop discount?",
            db=mock_db,
            model=mock_model,
            reranker=mock_reranker,
        )

    assert result.is_answer_supported is False
    assert result.sources == []
    assert "insufficient" in result.answer.lower()
    mock_generate.assert_not_called()


def test_rag_answers_supported_question():
    """Verify supported policy questions produce grounded answers."""

    chunks = [
        {
            "id": 1,
            "source": "office_loan_policy.pdf",
            "page_number": 3,
            "text": "Personal loans are limited to twice gross monthly salary.",
        }
    ]

    with (
        patch(
            "office_loan_policy_assistant.services.rag_service.hybrid_search",
            return_value=chunks,
        ),
        patch(
            "office_loan_policy_assistant.services.rag_service.rerank_chunks",
            return_value=chunks,
        ),
        patch(
            "office_loan_policy_assistant.services.rag_service.check_answerability",
        ) as mock_answerability,
        patch(
            "office_loan_policy_assistant.services.rag_service.generate_policy_answer",
            return_value="Personal loans are limited to twice gross monthly salary.",
        ),
        patch(
            "office_loan_policy_assistant.services.rag_service.validate_answer_evidence",
        ) as mock_validation,
    ):
        mock_answerability.return_value.is_answerable = True
        mock_validation.return_value.is_supported = True

        result = answer_policy_question(
            question="What is the maximum personal loan amount?",
            db=Mock(),
            model=Mock(),
            reranker=Mock(),
        )

    assert result.is_answer_supported is True
    assert len(result.sources) == 1
    assert result.sources[0].page_number == 3
    assert "twice gross monthly salary" in result.answer


def test_policy_api_handles_service_failure():
    """Verify the API handles RAG service failures safely."""

    client = TestClient(app)

    with patch(
        "office_loan_policy_assistant.api.policy.answer_policy_question_with_models",
        side_effect=RuntimeError("Simulated service failure"),
    ):
        response = client.post(
            "/policy/ask",
            json={
                "question": "What is the maximum personal loan amount?"
            },
        )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "The policy assistant is temporarily unavailable. "
            "Please try again later."
        )
    }