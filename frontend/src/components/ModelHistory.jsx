import { getModelHistory } from "../api/history";
import { useFetch } from "../hooks/useFetch";
import ErrorMessage from "./ErrorMessage";
import HistoryEntry from "./HistoryEntry";
import Spinner from "./Spinner";

// Sekcja „Historia zmian” na stronie szczegółów modelu
export default function ModelHistory({ modelId }) {
  const { data: entries, loading, error, reload } = useFetch(() => getModelHistory(modelId), [modelId]);

  return (
    <section className="history">
      <h3>Historia zmian</h3>
      {loading && !entries && <Spinner label="Ładowanie historii..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {entries && entries.length === 0 && <p className="muted">Brak zapisanych zmian.</p>}
      {entries && entries.length > 0 && (
        <ul className="history-list">
          {entries.map((entry) => (
            <HistoryEntry key={entry.id} entry={entry} />
          ))}
        </ul>
      )}
    </section>
  );
}
