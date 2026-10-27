import os
import logging
import time
from dotenv import load_dotenv
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError


load_dotenv()

logger = logging.getLogger(__name__)

def get_llm_client() -> OpenAI:
    """Create the Microsoft Foundry inference client."""

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    base_url = os.getenv("AZURE_OPENAI_BASE_URL")

    if not api_key or not base_url:
        raise ValueError(
            "Azure OpenAI API key or base URL is missing."
        )

    return OpenAI(
        api_key=api_key,
        base_url=base_url.rstrip("/") + "/",
        timeout=30.0,
        max_retries=1,
    )


def generate_policy_answer(
    question: str,
    context: str,
) -> str:
    """Generate an answer grounded in retrieved policy context."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context.strip():
        raise ValueError("Policy context cannot be empty.")

    client = get_llm_client()

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not deployment:
        raise ValueError("Azure OpenAI deployment is missing.")


    start_time = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an Office Loan Policy Assistant. "
                        "Answer questions using only the supplied policy context. "
                        "Do not invent policy rules, loan limits, or exceptions. "
                        "If the context does not contain enough information, "
                        "clearly state that the policy information is insufficient. "
                        "Include relevant document names and page numbers. "
                        "Never claim that a loan has been approved."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Policy context:\n{context}"
                    ),
                },
            ],
        )
    except (APITimeoutError, APIConnectionError):
        latency_ms = (time.perf_counter() - start_time) * 1000

        logger.error(
            "LLM request failed | failure_type=connection_or_timeout | "
            "latency_ms=%.2f",
            latency_ms,
        )
        raise

    except APIError:
        latency_ms = (time.perf_counter() - start_time) * 1000

        logger.error(
            "LLM request failed | failure_type=api_error | "
            "latency_ms=%.2f",
            latency_ms,
        )
        raise

    latency_ms = (time.perf_counter() - start_time) * 1000

    usage = response.usage

    logger.info(
        "LLM request completed | latency_ms=%.2f | "
        "prompt_tokens=%s | completion_tokens=%s | total_tokens=%s",
        latency_ms,
        usage.prompt_tokens if usage else None,
        usage.completion_tokens if usage else None,
        usage.total_tokens if usage else None,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise ValueError("The language model returned an empty answer.")

    return answer