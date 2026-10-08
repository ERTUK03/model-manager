// Tymczasowe dane. Zastąpi je plik JSON.
const MODELS = [
  { id: 1, name: "iris-classifier", description: "Klasyfikacja gatunków irysów", framework: "scikit-learn", task: "Klasyfikacja", version: "1.0.0", accuracy: 0.967, size_mb: 0.4, status: "published" },
  { id: 2, name: "house-price-regressor", description: "Predykcja cen mieszkań", framework: "XGBoost", task: "Regresja", version: "2.1.0", accuracy: 0.882, size_mb: 12.3, status: "published" },
  { id: 3, name: "mnist-cnn", description: "Rozpoznawanie cyfr pisanych ręcznie", framework: "TensorFlow", task: "Klasyfikacja obrazów", version: "1.3.0", accuracy: 0.992, size_mb: 8.7, status: "draft" },
];

const STATUS_LABELS = {
  draft: "Szkic",
  published: "Opublikowany",
  archived: "Zarchiwizowany",
};

function formatAccuracy(value) {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "—";
}

export default function ModelsPage() {
  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Framework</th>
            <th>Zadanie</th>
            <th>Wersja</th>
            <th>Dokładność</th>
            <th>Rozmiar</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {MODELS.map((m) => (
            <tr key={m.id}>
              <td>
                <strong>{m.name}</strong>
                <div className="muted small">{m.description}</div>
              </td>
              <td>{m.framework}</td>
              <td>{m.task}</td>
              <td>{m.version}</td>
              <td>{formatAccuracy(m.accuracy)}</td>
              <td>{m.size_mb} MB</td>
              <td>
                <span className={`badge badge-${m.status}`}>
                  {STATUS_LABELS[m.status] ?? m.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
