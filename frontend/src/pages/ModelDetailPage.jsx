import { Link, useParams } from "react-router-dom";
import { getModel } from "../api/models";
import StatusBadge from "../components/StatusBadge";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatDate, formatSize } from "../utils/format";

export default function ModelDetailPage() {
  const { id } = useParams();
  const { data: model, loading, error } = useFetch(() => getModel(id), [id]);

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
            <h2>{model.name}</h2>
            <StatusBadge status={model.status} />
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
