import time

from app.services.gemini_service import generate_gemini_answer
from app.services.grok_service import generate_grok_answer


def generate_rag_answer(
    question: str,
    search_results: list[dict],
) -> tuple[str, str]:
    if not search_results:
        return (
            "I could not find this information in the "
            "uploaded company documents.",
            "none",
        )

    # Try Gemini three times.
    for attempt in range(3):
        try:
            answer = generate_gemini_answer(
                question=question,
                search_results=search_results,
            )

            return answer, "gemini"

        except Exception as gemini_error:
            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{gemini_error}"
            )

            if attempt < 2:
                time.sleep(2 ** attempt)

    # Try Grok if Gemini fails.
    try:
        print("Trying Grok fallback...")

        answer = generate_grok_answer(
            question=question,
            search_results=search_results,
        )

        return answer, "grok"

    except Exception as grok_error:
        print(f"Grok fallback failed: {grok_error}")

        return (
            "The AI service is temporarily unavailable. "
            "Please try again in a few minutes.",
            "unavailable",
        )