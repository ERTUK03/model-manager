import { Link, useSearchParams } from "react-router-dom";
import { getHistory } from "../api/history";
import ErrorMessage from "../components/ErrorMessage";
import HistoryEntry from "../components/HistoryEntry";
import Pagination from "../components/Pagination";
import Spinner from "../components/Spinner";
import { ACTION_LABELS } from "../constants";
import { useFetch } from "../hooks/useFetch";

const PAGE_SIZE = 20;

function positiveInt(value) {
  const number = Number.parseInt(value, 10);
  return Number.isInteger(number) && number >= 1 ? number : 1;
}

// Dziennik zmian wszystkich modeli (także usuniętych), dostępny tylko dla administratora
export default function HistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const rawAction = searchParams.get("action");
  const action = rawAction in ACTION_LABELS ? rawAction : "";
  const page = positiveInt(searchParams.get("page"));
  const { data, loading, error, reload } = useFetch(() => getHistory({ action, page, pageSize: PAGE_SIZE }), [action, page]);

  function update(patch, { replace = true } = {}) {
    const next = { action, page, ...patch };
    const url = new URLSearchParams();
    if (next.action) url.set("action", next.action);
    if (next.page > 1) url.set("page", String(next.page));
    setSearchParams(url, { replace });
  }

  return (
    <section>
      <div className="page-header">
        <h2>Historia zmian</h2>
      </div>
      <form className="filters" onSubmit={(event) => event.preventDefault()}>
        <select aria-label="Rodzaj zmiany" value={action} onChange={(event) => update({ action: event.target.value, page: 1 })}>
          <option value="">Wszystkie zmiany</option>
          {Object.entries(ACTION_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </form>

      {loading && !data && <Spinner label="Ładowanie historii..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {data && data.total === 0 && <p className="muted">Brak zapisanych zmian.</p>}

      {data && data.total > 0 && (
        <>
          <ul className={`history-list${loading ? " is-loading" : ""}`}>
            {data.items.map((entry) => (
              <li key={entry.id} className="history-global-item">
                <p className="history-model">
                  {entry.action === "deleted" ? (
                    <strong>{entry.model_name}</strong>
                  ) : (
                    <Link to={`/models/${entry.model_id}`}>
                      <strong>{entry.model_name}</strong>
                    </Link>
                  )}
                </p>
                <ul>
                  <HistoryEntry entry={entry} />
                </ul>
              </li>
            ))}
          </ul>
          <Pagination
            page={data.page}
            pages={data.pages}
            total={data.total}
            pageSize={PAGE_SIZE}
            onPageChange={(next) => update({ page: next }, { replace: false })}
          />
        </>
      )}
    </section>
  );
}
