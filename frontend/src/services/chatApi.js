const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8001/api";

function getAuthorizationHeaders() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error(
      "Please log in to continue."
    );
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function readResponse(response) {
  let data;

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("access_token");

      throw new Error(
        "Your session expired. Please log in again."
      );
    }

    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to complete the request."
    );
  }

  return data;
}

export async function askQuestion(
  question,
  conversationId = null
) {
  const response = await fetch(
    `${API_BASE_URL}/chat/ask`,
    {
      method: "POST",
      headers: getAuthorizationHeaders(),
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
      }),
    }
  );

  return readResponse(response);
}

export async function getConversations() {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations`,
    {
      method: "GET",
      headers: getAuthorizationHeaders(),
    }
  );

  return readResponse(response);
}

export async function getConversation(
  conversationId
) {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations/${conversationId}`,
    {
      method: "GET",
      headers: getAuthorizationHeaders(),
    }
  );

  return readResponse(response);
}

export async function deleteConversation(
  conversationId
) {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations/${conversationId}`,
    {
      method: "DELETE",
      headers: getAuthorizationHeaders(),
    }
  );

  return readResponse(response);
}