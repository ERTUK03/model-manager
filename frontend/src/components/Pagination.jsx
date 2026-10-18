import { PAGE_SIZES } from "../utils/listParams";

export default function Pagination({ page, pages, total, pageSize, onPageChange, onPageSizeChange }) {
  const lastPage = Math.max(1, pages);

  return (
    <nav className="pagination" aria-label="Paginacja">
      <span className="muted">Razem: {total}</span>
      <div className="pagination-controls">
        <button type="button" className="btn btn-secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          ← Poprzednia
        </button>
        <span>
          Strona {page} z {lastPage}
        </span>
        <button type="button" className="btn btn-secondary" disabled={page >= lastPage} onClick={() => onPageChange(page + 1)}>
          Następna →
        </button>
      </div>
      {onPageSizeChange && (
        <label className="page-size">
          Na stronie
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}>
            {PAGE_SIZES.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>
      )}
    </nav>
  );
}
