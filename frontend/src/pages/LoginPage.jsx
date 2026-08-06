import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../services/authApi";
import { checkAdminAccess } from "../services/adminApi";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

 async function handleSubmit(event) {
  event.preventDefault();

  if (!email.trim() || !password) {
    setError("Please enter your email and password.");
    return;
  }

  setError("");
  setIsLoading(true);

  try {
    await loginUser(email.trim(), password);

    await loginUser(email.trim(), password);

try {
  await checkAdminAccess();
  navigate("/admin", { replace: true });
} catch {
  navigate("/chat", { replace: true });
}
  } catch (requestError) {
    setError(requestError.message);
  } finally {
    setIsLoading(false);
  }
}

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-logo">KB</div>

        <h1>Welcome Back</h1>

        <p className="login-description">
          Sign in to access the Company Knowledge Assistant.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="name@company.com"
            autoComplete="email"
          />

          <label htmlFor="password">Password</label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
          />

          {error && <div className="login-error">{error}</div>}

          <button type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="auth-link">
  Do not have an account?{" "}
  <Link to="/register">Create account</Link>
</p>
      </section>
    </main>
  );
}

export default LoginPage;