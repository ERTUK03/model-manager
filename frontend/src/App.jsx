import { Link, Route, Routes, useNavigate } from "react-router-dom";
import AdminRoute from "./components/AdminRoute";
import ProtectedRoute from "./components/ProtectedRoute";
import { ROLE_LABELS } from "./constants";
import { useAuth } from "./context/AuthContext";
import { useToast } from "./context/ToastContext";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import ModelDetailPage from "./pages/ModelDetailPage";
import ModelFormPage from "./pages/ModelFormPage";
import ModelsPage from "./pages/ModelsPage";
import NotFoundPage from "./pages/NotFoundPage";
import RegisterPage from "./pages/RegisterPage";

export default function App() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  function handleLogout() {
    logout();
    toast.success("Wylogowano.");
    navigate("/login");
  }

  return (
    <div className="container">
      <header className="topbar">
        <div>
          <Link to="/" className="brand">
            <h1>Model Manager</h1>
          </Link>
          <p className="muted">Katalog zapisanych modeli uczenia maszynowego</p>
        </div>
        {user ? (
          <div className="userbox">
            {isAdmin && <Link to="/history">Historia zmian</Link>}
            <span>{user.email}</span>
            <span className="role-badge">{ROLE_LABELS[user.role] ?? user.role}</span>
            <button type="button" className="btn btn-secondary" onClick={handleLogout}>
              Wyloguj
            </button>
          </div>
        ) : (
          <nav className="userbox">
            <Link to="/login">Zaloguj się</Link>
            <Link to="/register">Utwórz konto</Link>
          </nav>
        )}
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<ModelsPage />} />
            <Route path="/models/:id" element={<ModelDetailPage />} />
            <Route element={<AdminRoute />}>
              <Route path="/models/new" element={<ModelFormPage />} />
              <Route path="/models/:id/edit" element={<ModelFormPage />} />
              <Route path="/history" element={<HistoryPage />} />
            </Route>
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  );
}
