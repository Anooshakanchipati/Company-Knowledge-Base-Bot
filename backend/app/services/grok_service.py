import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

xai_api_key = os.getenv("XAI_API_KEY")
grok_model = os.getenv("GROK_MODEL", "grok-4.5")


def generate_grok_answer(
    question: str,
    search_results: list[dict],
) -> str:
    if not search_results:
        return (
            "I could not find this information in the "
            "uploaded company documents."
        )

    if not xai_api_key:
        raise RuntimeError(
            "XAI_API_KEY is missing from the .env file"
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
1. Answer only from the document context below.
2. Do not use outside knowledge.
3. Do not invent company information.
4. Give a clear and simple answer.
5. If the answer is unavailable, say:
   "I could not find this information in the uploaded company documents."

Document context:
{context}

User question:
{question}

Answer:
""".strip()

    grok_client = OpenAI(
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
    )

    response = grok_client.responses.create(
        model=grok_model,
        input=prompt,
    )

    answer = response.output_text

    if not answer:
        raise ValueError("Grok returned an empty answer")

    return answer.strip()