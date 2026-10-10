import { Link } from "react-router-dom";
import { deleteModel, getModels } from "../api/models";
import StatusBadge from "../components/StatusBadge";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatSize } from "../utils/format";

export default function ModelsPage() {
  const { data: models, loading, error, reload } = useFetch(getModels);

  async function handleDelete(model) {
    if (!window.confirm(`Usunąć model „${model.name}”?`)) return;
    try {
      await deleteModel(model.id);
      reload();
    } catch (err) {
      window.alert(err.message);
    }
  }

  return (
    <section>
      <div className="page-header">
        <h2>Modele</h2>
        <Link to="/models/new" className="btn btn-primary">
          Dodaj model
        </Link>
      </div>

      {loading && <p className="muted">Ładowanie...</p>}
      {error && <p className="error">{error.message}</p>}
      {models && models.length === 0 && <p className="muted">Brak modeli do wyświetlenia.</p>}

      {models && models.length > 0 && (
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
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id}>
                  <td>
                    <Link to={`/models/${m.id}`}>
                      <strong>{m.name}</strong>
                    </Link>
                    <div className="muted small">{m.description}</div>
                  </td>
                  <td>{m.framework}</td>
                  <td>{m.task}</td>
                  <td>{m.version}</td>
                  <td>{formatAccuracy(m.accuracy)}</td>
                  <td>{formatSize(m.size_mb)}</td>
                  <td>
                    <StatusBadge status={m.status} />
                  </td>
                  <td className="actions">
                    <Link to={`/models/${m.id}/edit`}>Edytuj</Link>
                    <button type="button" className="link-danger" onClick={() => handleDelete(m)}>
                      Usuń
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
