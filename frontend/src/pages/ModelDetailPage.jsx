import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteModel, getModel } from "../api/models";
import StatusBadge from "../components/StatusBadge";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatDate, formatSize } from "../utils/format";

export default function ModelDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: model, loading, error } = useFetch(() => getModel(id), [id]);

  async function handleDelete() {
    if (!window.confirm(`Usunąć model „${model.name}”?`)) return;
    try {
      await deleteModel(id);
      navigate("/");
    } catch (err) {
      window.alert(err.message);
    }
  }

  return (
    <section>
      <p>
        <Link to="/">← Wróć do listy</Link>
      </p>

      {loading && <p className="muted">Ładowanie...</p>}
      {error && <p className="error">{error.message}</p>}

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
              <button type="button" className="btn btn-danger" onClick={handleDelete}>
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
        </>
      )}
    </section>
  );
}
