import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteModel, getModel } from "../api/models";
import ConfirmDialog from "../components/ConfirmDialog";
import ErrorMessage from "../components/ErrorMessage";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../context/ToastContext";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatDate, formatSize } from "../utils/format";

export default function ModelDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const { data: model, loading, error, reload } = useFetch(() => getModel(id), [id]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function confirmDelete() {
    setDeleting(true);
    try {
      await deleteModel(id);
      toast.success(`Model „${model.name}” został usunięty.`);
      navigate("/");
    } catch (err) {
      toast.error(err.message);
      setDeleting(false);
    }
  }

  return (
    <section>
      <p>
        <Link to="/">← Wróć do listy</Link>
      </p>

      {loading && <Spinner label="Ładowanie modelu..." />}
      {error && <ErrorMessage error={error} onRetry={error.status === 404 ? undefined : reload} />}

      {model && (
        <>
          <div className="page-header">
            <h2>
              {model.name} <StatusBadge status={model.status} />
            </h2>
            <div className="button-group">
              <Link to={`/models/${id}/edit`} className="btn btn-secondary">
                Edytuj
              </Link>
              <button type="button" className="btn btn-danger" onClick={() => setConfirmOpen(true)}>
                Usuń
              </button>
            </div>
          </div>
          {model.description && <p>{model.description}</p>}

          <dl className="details">
            <dt>Framework</dt>
            <dd>{model.framework}</dd>
            <dt>Zadanie</dt>
            <dd>{model.task}</dd>
            <dt>Wersja</dt>
            <dd>{model.version}</dd>
            <dt>Dokładność</dt>
            <dd>{formatAccuracy(model.accuracy)}</dd>
            <dt>Rozmiar</dt>
            <dd>{formatSize(model.size_mb)}</dd>
            <dt>Utworzono</dt>
            <dd>{formatDate(model.created_at)}</dd>
            <dt>Ostatnia zmiana</dt>
            <dd>{formatDate(model.updated_at)}</dd>
          </dl>

          <ConfirmDialog
            open={confirmOpen}
            title="Usunąć model?"
            message={`Model „${model.name}” zostanie trwale usunięty.`}
            confirmLabel="Usuń"
            busy={deleting}
            onConfirm={confirmDelete}
            onCancel={() => setConfirmOpen(false)}
          />
        </>
      )}
    </section>
  );
}
