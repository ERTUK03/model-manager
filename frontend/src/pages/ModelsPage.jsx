import { useState } from "react";
import { Link } from "react-router-dom";
import { deleteModel, getModels } from "../api/models";
import ConfirmDialog from "../components/ConfirmDialog";
import ErrorMessage from "../components/ErrorMessage";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../context/ToastContext";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatSize } from "../utils/format";

export default function ModelsPage() {
  const { data: models, loading, error, reload } = useFetch(getModels);
  const toast = useToast();
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  async function confirmDelete() {
    setDeleting(true);
    try {
      await deleteModel(toDelete.id);
      toast.success(`Model „${toDelete.name}” został usunięty.`);
      setToDelete(null);
      reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setDeleting(false);
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

      {loading && <Spinner label="Ładowanie modeli..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}

      {models && models.length === 0 && (
        <div className="empty-state">
          <p>Nie ma jeszcze żadnych modeli.</p>
          <Link to="/models/new" className="btn btn-primary">
            Dodaj pierwszy model
          </Link>
        </div>
      )}

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
                    <button type="button" className="link-danger" onClick={() => setToDelete(m)}>
                      Usuń
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(toDelete)}
        title="Usunąć model?"
        message={toDelete ? `Model „${toDelete.name}” zostanie trwale usunięty.` : ""}
        confirmLabel="Usuń"
        busy={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setToDelete(null)}
      />
    </section>
  );
}
