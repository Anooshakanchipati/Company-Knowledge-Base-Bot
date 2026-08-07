import time
from app.services.gemini_service import (
    generate_gemini_answer,
)
from app.services.grok_service import (
    generate_grok_answer,
)

def generate_rag_answer(
    question: str,
    search_results: list[dict],
) -> str:
    if not search_results:
        return (
            "I could not find this information in the "
            "uploaded company documents."
        )

    # Try Gemini three times.
    for attempt in range(3):
        try:
            return generate_gemini_answer(
                question,
                search_results,
            )
        except Exception as gemini_error:
            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{gemini_error}"
            )

            if attempt < 2:
                time.sleep(2 ** attempt)

    # Try Grok after all Gemini attempts fail.
    try:
        answer = generate_gemini_answer(
        question,
        search_results,
    )
    except Exception as gemini_error:
         print(f"Gemini failed: {gemini_error}")

    try:
        print("Trying Grok fallback...")

        answer = generate_grok_answer(
            question,
            search_results,
        )
    except Exception as grok_error:
        print(f"Grok fallback failed: {grok_error}")

        answer = (
            "The AI service is temporarily unavailable. "
            "Please try again in a few minutes."
        )

    return answer