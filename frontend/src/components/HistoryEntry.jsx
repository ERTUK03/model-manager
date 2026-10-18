import { ACTION_LABELS } from "../constants";
import { describeChanges, formatAuthor } from "../utils/history";
import { formatDate } from "../utils/format";

// Jeden wpis historii: akcja, autor, data i lista zmienionych pól
export default function HistoryEntry({ entry }) {
  const changes = entry.action === "updated" ? describeChanges(entry.changes) : [];

  return (
    <li className="history-entry">
      <div className="history-head">
        <span className={`badge badge-action-${entry.action}`}>{ACTION_LABELS[entry.action] ?? entry.action}</span>
        <span className="muted small">
          {formatDate(entry.created_at)} · {formatAuthor(entry.user_email)}
        </span>
      </div>
      {entry.action === "created" && <p className="history-text">Model został dodany do katalogu.</p>}
      {entry.action === "deleted" && <p className="history-text">Model został usunięty.</p>}
      {changes.length > 0 && (
        <ul className="history-changes">
          {changes.map((change) => (
            <li key={change.field}>
              <strong>{change.label}:</strong> {change.from} → {change.to}
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}
