from app.services.gemini_service import (
    generate_gemini_answer,
)
from app.services.grok_service import (
    generate_grok_answer,
)


def generate_rag_answer(
    question: str,
    search_results: list[dict],
) -> tuple[str, str]:
    try:
        answer = generate_gemini_answer(
            question=question,
            search_results=search_results,
        )

        return answer, "gemini"

    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")
        print("Trying Grok fallback...")

        answer = generate_grok_answer(
            question=question,
            search_results=search_results,
        )

        return answer, "grok"