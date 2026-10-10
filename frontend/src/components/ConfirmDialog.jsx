export default function ConfirmDialog({ open, title, message, confirmLabel = "Potwierdź", busy = false, onConfirm, onCancel }) {
  if (!open) return null;

  return (
    <div className="overlay" onClick={busy ? undefined : onCancel}>
      <div className="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title" onClick={(e) => e.stopPropagation()}>
        <h3 id="dialog-title">{title}</h3>
        <p>{message}</p>
        <div className="button-group dialog-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={busy}>
            Anuluj
          </button>
          <button type="button" className="btn btn-danger-solid" onClick={onConfirm} disabled={busy}>
            {busy ? "Usuwanie..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
