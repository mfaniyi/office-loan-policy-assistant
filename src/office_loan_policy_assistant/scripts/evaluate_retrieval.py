from pathlib import Path
import runpy

from office_loan_policy_assistant.db.database import SessionLocal
from office_loan_policy_assistant.services.embedding_service import (
    load_embedding_model,
)
from office_loan_policy_assistant.services.hybrid_search_service import (
    hybrid_search,
)
from office_loan_policy_assistant.services.reranking_service import (
    load_reranker,
    rerank_chunks,
)


def evaluate_retrieval() -> None:
    """Evaluate whether expected policy pages appear in the top three."""

    dataset_path = Path("tests/retrieval_questions.py")
    questions = runpy.run_path(str(dataset_path))["RETRIEVAL_QUESTIONS"]

    model = load_embedding_model()
    reranker = load_reranker()

    hits = 0
    top1_hits = 0
    relevant_top1_hits = 0
    text_hits = 0
    text_evaluated = 0

    with SessionLocal() as db:
        for item in questions:
            candidates = hybrid_search(
                question=item["question"],
                db=db,
                model=model,
                limit=10,
            )

            results = rerank_chunks(
                question=item["question"],
                chunks=candidates,
                model=reranker,
                limit=3,
            )

            retrieved_pages = [r["page_number"] for r in results]
            hit = item["expected_page"] in retrieved_pages

            hits += int(hit)

            top1_hit = bool(results) and results[0]["page_number"] == item["expected_page"]

            top1_hits += int(top1_hit)

            relevant_pages = item.get(
                "relevant_pages",
                [item["expected_page"]],
            )

            relevant_top1_hit = (
                bool(results)
                and results[0]["page_number"] in relevant_pages
            )

            relevant_top1_hits += int(relevant_top1_hit)

            required_text = item.get("required_text")

            if required_text:
                text_evaluated += 1

                text_found = any(
                    required_text.casefold() in result["text"].casefold()
                    for result in results
                )

                text_hits += int(text_found)

                print(
                    f"TEXT {'HIT' if text_found else 'MISS'} | "
                    f"{item['question']}"
                )

            print(
                f"{'HIT' if hit else 'MISS'} | "
                f"Expected: {item['expected_page']} | "
                f"Retrieved: {retrieved_pages} | "
                f"{item['question']}"
            )

    total = len(questions)
    hit_rate = hits / total if total else 0

    print(f"\nHit@3: {hits}/{total} ({hit_rate:.1%})")

    top1_rate = top1_hits / total if total else 0

    print(f"Hit@1: {top1_hits}/{total} ({top1_rate:.1%})")

    relevant_top1_rate = relevant_top1_hits / total if total else 0

    print(
        f"Relevant Hit@1: {relevant_top1_hits}/{total} "
        f"({relevant_top1_rate:.1%})"
    )

    text_hit_rate = (
        text_hits / text_evaluated
        if text_evaluated
        else 0
    )

    print(
        f"Text Hit@3: {text_hits}/{text_evaluated} "
        f"({text_hit_rate:.1%})"
    )

if __name__ == "__main__":
    evaluate_retrieval()