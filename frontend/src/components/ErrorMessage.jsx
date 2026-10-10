export default function ErrorMessage({ error, onRetry }) {
  return (
    <div className="error-box" role="alert">
      <strong>{error?.message ?? "Wystąpił nieoczekiwany błąd."}</strong>
      {onRetry && (
        <div>
          <button type="button" className="btn btn-secondary retry" onClick={onRetry}>
            Spróbuj ponownie
          </button>
        </div>
      )}
    </div>
  );
}
