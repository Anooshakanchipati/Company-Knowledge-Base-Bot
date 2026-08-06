import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import RegisterPage from "./pages/RegisterPage";
import AdminRoute from "./components/AdminRoute";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import { isLoggedIn } from "./services/authApi";
import AdminPage from "./pages/AdminPage";
import DashboardPage from "./pages/DashboardPage";

function ProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
  path="/chat"
  element={
    <ProtectedRoute>
      <ChatPage />
    </ProtectedRoute>
  }
/>
<Route
  path="/admin"
  element={
    <ProtectedRoute>
      <AdminRoute>
        <AdminPage />
      </AdminRoute>
    </ProtectedRoute>
  }
/>
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  }
/>
      <Route
  path="/admin"
  element={
    <ProtectedRoute>
      <AdminPage />
    </ProtectedRoute>
  }
/>

      <Route
        path="/register"
        element={<RegisterPage />}
      />

      <Route
         path="*"
  element={
    <Navigate
      to={isLoggedIn() ? "/dashboard" : "/login"}
      replace
          />
        }
      />
    </Routes>
    
  );
}

export default App;