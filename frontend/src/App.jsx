import { Link, Route, Routes } from "react-router-dom";
import ModelDetailPage from "./pages/ModelDetailPage";
import ModelsPage from "./pages/ModelsPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  return (
    <div className="container">
      <header className="header">
        <Link to="/" className="brand">
          <h1>Model Manager</h1>
        </Link>
        <p className="muted">Katalog zapisanych modeli uczenia maszynowego</p>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<ModelsPage />} />
          <Route path="/models/:id" element={<ModelDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  );
}
