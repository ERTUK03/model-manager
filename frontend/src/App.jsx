import ModelsPage from "./pages/ModelsPage";

export default function App() {
  return (
    <div className="container">
      <header className="header">
        <h1>Model Manager</h1>
        <p className="muted">Katalog zapisanych modeli uczenia maszynowego</p>
      </header>
      <main>
        <ModelsPage />
      </main>
    </div>
  );
}
