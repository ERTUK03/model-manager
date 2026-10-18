import { Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ForbiddenPage from "../pages/ForbiddenPage";

// Używana wewnątrz ProtectedRoute: zwykły użytkownik zobaczy komunikat zamiast formularza
export default function AdminRoute() {
  const { isAdmin } = useAuth();
  return isAdmin ? <Outlet /> : <ForbiddenPage />;
}
