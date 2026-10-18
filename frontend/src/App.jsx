import { Link, Route, Routes, useNavigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import { useToast } from "./context/ToastContext";
import LoginPage from "./pages/LoginPage";
import ModelDetailPage from "./pages/ModelDetailPage";
import ModelFormPage from "./pages/ModelFormPage";
import ModelsPage from "./pages/ModelsPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  const { user, logout } = useAuth();
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
        {user && (
          <div className="userbox">
            <span>{user.email}</span>
            <button type="button" className="btn btn-secondary" onClick={handleLogout}>
              Wyloguj
            </button>
          </div>
        )}
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<ModelsPage />} />
            <Route path="/models/new" element={<ModelFormPage />} />
            <Route path="/models/:id" element={<ModelDetailPage />} />
            <Route path="/models/:id/edit" element={<ModelFormPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  );
}
