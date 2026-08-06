import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getCurrentUser,
  logoutUser,
} from "../services/authApi";
import "./DashboardPage.css";

function DashboardPage() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
  async function loadCurrentUser() {
    try {
      setIsLoading(true);
      setError("");

      const data = await getCurrentUser();
      setUser(data);
    } catch (requestError) {
      setError(requestError.message);

      if (!localStorage.getItem("access_token")) {
        navigate("/login", { replace: true });
      }
    } finally {
      setIsLoading(false);
    }
  }

  loadCurrentUser();
}, [navigate]);

  function handleLogout() {
    logoutUser();
    navigate("/login", { replace: true });
  }

  const isAdmin =
    user?.role?.toLowerCase() === "admin" ||
    user?.is_admin === true;

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <div className="dashboard-logo">K</div>

          <div>
            <h1>Company Knowledge Base</h1>
            <p>Your AI-powered company information assistant</p>
          </div>
        </div>

        <button
          type="button"
          className="logout-button"
          onClick={handleLogout}
        >
          Logout
        </button>
      </header>

      <main className="dashboard-content">
        {isLoading && (
          <div className="dashboard-status">
            Loading your dashboard...
          </div>
        )}

        {error && (
          <div className="dashboard-error">{error}</div>
        )}

        {!isLoading && user && (
          <>
            <section className="welcome-section">
              <div>
                <span className="welcome-label">Welcome back</span>

                <h2>{user.name || "User"} 👋</h2>

                <p>
                  Search company information, continue previous
                  conversations, and manage your account.
                </p>
              </div>

              <div className="user-summary">
                <div className="user-avatar">
                  {(user.name || user.email || "U")
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <div>
                  <strong>{user.name || "User"}</strong>
                  <span>{user.email}</span>

                  <small className={isAdmin ? "admin-role" : ""}>
                    {isAdmin ? "Administrator" : "User"}
                  </small>
                </div>
              </div>
            </section>

            <section className="dashboard-cards">
              <button
                type="button"
                className="dashboard-card"
                onClick={() => navigate("/chat")}
              >
                <span className="card-icon">💬</span>
                <h3>AI Chat</h3>
                <p>
                  Ask questions and receive answers from company
                  documents.
                </p>
                <strong className="card-link">Start chatting →</strong>
              </button>

              <button
                type="button"
                className="dashboard-card"
                onClick={() => navigate("/chat")}
              >
                <span className="card-icon">🕘</span>
                <h3>Chat History</h3>
                <p>
                  Open previous conversations and continue where
                  you stopped.
                </p>
                <strong className="card-link">View history →</strong>
              </button>

              <article className="dashboard-card profile-card">
                <span className="card-icon">👤</span>
                <h3>My Profile</h3>

                <div className="profile-details">
                  <p>
                    <strong>Name:</strong> {user.name || "Not available"}
                  </p>

                  <p>
                    <strong>Email:</strong> {user.email}
                  </p>

                  <p>
                    <strong>Role:</strong>{" "}
                    {isAdmin ? "Administrator" : user.role || "User"}
                  </p>
                </div>
              </article>

              {isAdmin && (
                <button
                  type="button"
                  className="dashboard-card admin-card"
                  onClick={() => navigate("/admin")}
                >
                  <span className="card-icon">📄</span>
                  <h3>Document Management</h3>
                  <p>
                    Upload, view, search, and delete company
                    documents.
                  </p>
                  <strong className="card-link">
                    Manage documents →
                  </strong>
                </button>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default DashboardPage;