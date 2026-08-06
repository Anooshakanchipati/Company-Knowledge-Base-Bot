import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getCurrentUser } from "../services/authApi";

function AdminRoute({ children }) {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    async function checkAdminAccess() {
      try {
        const user = await getCurrentUser();

        const isAdmin =
          user?.role?.toLowerCase() === "admin" ||
          user?.is_admin === true;

        setStatus(isAdmin ? "allowed" : "denied");
      } catch {
        setStatus("unauthorized");
      }
    }

    checkAdminAccess();
  }, []);

  if (status === "loading") {
    return <p style={{ padding: "30px" }}>Checking admin access...</p>;
  }

  if (status === "unauthorized") {
    return <Navigate to="/login" replace />;
  }

  if (status === "denied") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default AdminRoute;