const API_BASE_URL = "http://127.0.0.1:8001/api";


async function readResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Something went wrong."
    );
  }

  return data;
}
export async function getCurrentUser() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please log in again.");
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    if (response.status === 401) {
      logoutUser();
    }

    throw new Error(data.detail || "Unable to load user details.");
  }

  return data;
}

export async function registerUser(name, email, password) {
  const response = await fetch(
    `${API_BASE_URL}/auth/register`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        email,
        password,
      }),
    }
  );

  return readResponse(response);
}

export async function loginUser(email, password) {
  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

  const data = await readResponse(response);

  localStorage.setItem(
    "access_token",
    data.access_token
  );

  return data;
}

export function logoutUser() {
  localStorage.removeItem("access_token");
}

export function isLoggedIn() {
  return Boolean(
    localStorage.getItem("access_token")
  );
}

export function getAccessToken() {
  return localStorage.getItem("access_token");
}