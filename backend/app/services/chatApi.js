const API_BASE_URL = "http://127.0.0.1:8001/api";

export async function askQuestion(
  question,
  conversationId = null
) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please log in before asking a question.");
  }

  const response = await fetch(`${API_BASE_URL}/chat/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Unable to generate the answer."
    );
  }

  return data;
}