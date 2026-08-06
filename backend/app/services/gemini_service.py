import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file"
    )

client = genai.Client(api_key=gemini_api_key)


def generate_gemini_answer(
    question: str,
    search_results: list[dict],
) -> str:
    if not search_results:
        return (
            "I could not find this information in the "
            "uploaded company documents."
        )

    context_sections = []

    for index, result in enumerate(search_results, start=1):
        context_sections.append(
            f"""
Source {index}
Document: {result["document_name"]}
Chunk: {result["chunk_number"]}
Content:
{result["content"]}
""".strip()
        )

    context = "\n\n".join(context_sections)

    prompt = f"""
You are a Company Knowledge Base Assistant.

Rules:
1. Answer only from the document context given below.
2. Do not use outside knowledge.
3. If the context does not contain the answer, say:
   "I could not find this information in the uploaded company documents."
4. Give a clear and simple answer.
5. Do not invent company policies or details.

Document context:
{context}

User question:
{question}

Answer:
""".strip()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    answer = response.text

    if not answer:
        raise ValueError("Gemini returned an empty answer")

    return answer.strip()