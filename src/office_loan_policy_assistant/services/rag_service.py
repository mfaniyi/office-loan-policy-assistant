from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from office_loan_policy_assistant.services.retrieval_service import (
    retrieve_policy_chunks,
)
from office_loan_policy_assistant.services.hybrid_search_service import (
    hybrid_search,
)
from office_loan_policy_assistant.services.reranking_service import (
    rerank_chunks,
    load_reranker,
)
from office_loan_policy_assistant.services.embedding_service import (
    load_embedding_model,
)
from office_loan_policy_assistant.services.evidence_service import (
    validate_answer_evidence,
)
from office_loan_policy_assistant.schemas.rag import (
    PolicyAnswerResponse,
    PolicySource,
)
from office_loan_policy_assistant.services.llm_service import (
    generate_policy_answer,
)
from office_loan_policy_assistant.services.answerability_service import (
    check_answerability,
)




def build_rag_context(chunks: list[dict]) -> str:
    """Format retrieved policy chunks for question answering."""

    if not chunks:
        return "No relevant policy information was retrieved."

    sections = []

    for index, chunk in enumerate(chunks, start=1):
        sections.append(
            f"[Source {index}]\n"
            f"Document: {chunk['source']}\n"
            f"Page: {chunk['page_number']}\n"
            f"Content:\n{chunk['text']}"
        )

    return "\n\n".join(sections)


def retrieve_rag_context(
    question: str,
    db: Session,
    model: SentenceTransformer,
    reranker: CrossEncoder,
    limit: int = 3,
) -> str:
    """Build RAG context using hybrid search and reranking."""

    candidates = hybrid_search(
        question=question,
        db=db,
        model=model,
        limit=10,
    )

    ranked_chunks = rerank_chunks(
        question=question,
        chunks=candidates,
        model=reranker,
        limit=limit,
    )

    return build_rag_context(ranked_chunks)


def answer_policy_question(
    question: str,
    db: Session,
    model: SentenceTransformer,
    reranker: CrossEncoder,
) -> PolicyAnswerResponse:
    """Answer a policy question using retrieved evidence."""

    candidates = hybrid_search(
        question=question,
        db=db,
        model=model,
        limit=10,
    )

    ranked_chunks = rerank_chunks(
        question=question,
        chunks=candidates,
        model=reranker,
        limit=3,
    )

    if not ranked_chunks:
        return PolicyAnswerResponse(
            question=question,
            answer="No relevant policy information was found.",
            sources=[],
        )

    context = build_rag_context(ranked_chunks)

    answerability = check_answerability(
        question=question,
        context=context,
    )

    if not answerability.is_answerable:
        return PolicyAnswerResponse(
            question=question,
            answer=(
                "The available Office Loan Policy information is insufficient "
                "to answer this question."
            ),
            sources=[],
            is_answer_supported=False,
        )

    answer = generate_policy_answer(
        question=question,
        context=context,
    )

    validation = validate_answer_evidence(
        question=question,
        answer=answer,
        context=context,
    )

    if not validation.is_supported:
        answer = (
            "The available Office Loan Policy information is insufficient "
            "to provide a verified answer to this question."
        )

    seen_sources = set()
    sources = []

    for chunk in ranked_chunks:
        source_key = (chunk["source"], chunk["page_number"])

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            sources.append(
                PolicySource(
                    document=chunk["source"],
                    page_number=chunk["page_number"],
                )
            )

    return PolicyAnswerResponse(
        question=question,
        answer=answer,
        sources=sources if validation.is_supported else [],
        is_answer_supported=validation.is_supported,
    )


def answer_policy_question_with_models(
    question: str,
    db: Session,
) -> PolicyAnswerResponse:
    """Answer a policy question using the complete RAG pipeline."""

    embedding_model = load_embedding_model()
    reranker = load_reranker()

    return answer_policy_question(
        question=question,
        db=db,
        model=embedding_model,
        reranker=reranker,
    )