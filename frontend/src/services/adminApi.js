const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8001/api";

function getHeaders() {
  const token = localStorage.getItem("access_token");

  return {
    Authorization: `Bearer ${token}`,
  };
}

async function readResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "Admin request failed.";

    throw new Error(message);
  }

  return data;
}

export async function checkAdminAccess() {
  const response = await fetch(
    `${API_BASE_URL}/admin/check`,
    {
      headers: getHeaders(),
    }
  );

  return readResponse(response);
}

export async function getDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/admin/documents`,
    {
      headers: getHeaders(),
    }
  );

  return readResponse(response);
}

export async function uploadDocuments(files) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(
    `${API_BASE_URL}/admin/documents/upload`,
    {
      method: "POST",
      headers: getHeaders(),
      body: formData,
    }
  );

  return readResponse(response);
}

export async function deleteDocument(documentId) {
  const response = await fetch(
    `${API_BASE_URL}/admin/documents/${documentId}`,
    {
      method: "DELETE",
      headers: getHeaders(),
    }
  );

  return readResponse(response);
}