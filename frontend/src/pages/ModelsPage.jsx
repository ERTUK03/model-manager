import { useEffect, useState } from "react";
import { getModels } from "../api/models";

const STATUS_LABELS = {
  draft: "Szkic",
  published: "Opublikowany",
  archived: "Zarchiwizowany",
};

function formatAccuracy(value) {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "—";
}

export default function ModelsPage() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getModels()
      .then(setModels)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Ładowanie...</p>;
  if (error) return <p className="error">{error}</p>;
  if (models.length === 0) return <p className="muted">Brak modeli do wyświetlenia.</p>;

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
          {models.map((m) => (
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
