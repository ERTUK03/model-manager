import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { deleteModel, getModels } from "../api/models";
import ConfirmDialog from "../components/ConfirmDialog";
import DownloadButton from "../components/DownloadButton";
import ErrorMessage from "../components/ErrorMessage";
import Pagination from "../components/Pagination";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { FRAMEWORKS, STATUS_LABELS, STATUSES } from "../constants";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useFetch } from "../hooks/useFetch";
import { formatAccuracy, formatBytes, formatSize } from "../utils/format";
import { hasActiveFilters, parseListParams, SORT_OPTIONS, toApiQuery, toUrlParams } from "../utils/listParams";

const SEARCH_DEBOUNCE_MS = 400;

export default function ModelsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  // Stan listy (wyszukiwanie, filtry, strona) żyje w adresie URL: odświeżenie i przycisk „wstecz” go zachowują
  const params = useMemo(() => parseListParams(searchParams), [searchParams]);
  const { data, loading, error, reload } = useFetch(() => getModels(params), [toApiQuery(params)]);
  const toast = useToast();
  const { isAdmin } = useAuth();
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [searchText, setSearchText] = useState(params.search);

  function updateParams(patch, { replace = true } = {}) {
    setSearchParams((previous) => toUrlParams({ ...parseListParams(previous), ...patch }), { replace });
  }

  // Adres zmienił się z zewnątrz (np. „Wyczyść filtry”): synchronizujemy pole, nie gubiąc spacji wpisywanych w trakcie
  useEffect(() => {
    setSearchText((current) => (current.trim() === params.search ? current : params.search));
  }, [params.search]);

  // Wyszukiwanie po krótkiej przerwie w pisaniu, żeby nie wysyłać zapytania po każdej literze
  useEffect(() => {
    const trimmed = searchText.trim();
    if (trimmed === params.search) return undefined;
    const timer = setTimeout(() => updateParams({ search: trimmed, page: 1 }), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchText]);

  // Po usunięciu ostatniego elementu ostatniej strony wracamy na poprzednią
  useEffect(() => {
    if (data && data.items.length === 0 && data.total > 0 && params.page > data.pages) {
      updateParams({ page: data.pages });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  function clearFilters() {
    updateParams({ search: "", framework: "", status: "", page: 1 });
  }

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

  const filtersActive = hasActiveFilters(params);

  return (
    <section>
      <div className="page-header">
        <h2>Modele</h2>
        {isAdmin && (
          <Link to="/models/new" className="btn btn-primary">
            Dodaj model
          </Link>
        )}
      </div>

      <form className="filters" role="search" onSubmit={(event) => event.preventDefault()}>
        <input
          type="search"
          aria-label="Szukaj"
          placeholder="Szukaj po nazwie lub opisie"
          value={searchText}
          onChange={(event) => setSearchText(event.target.value)}
        />
        <select
          aria-label="Framework"
          value={params.framework}
          onChange={(event) => updateParams({ framework: event.target.value, page: 1 })}
        >
          <option value="">Wszystkie frameworki</option>
          {FRAMEWORKS.map((framework) => (
            <option key={framework} value={framework}>
              {framework}
            </option>
          ))}
        </select>
        <select
          aria-label="Status"
          value={params.status}
          onChange={(event) => updateParams({ status: event.target.value, page: 1 })}
        >
          <option value="">Wszystkie statusy</option>
          {STATUSES.map((status) => (
            <option key={status} value={status}>
              {STATUS_LABELS[status]}
            </option>
          ))}
        </select>
        <select aria-label="Sortowanie" value={params.sort} onChange={(event) => updateParams({ sort: event.target.value, page: 1 })}>
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {filtersActive && (
          <button type="button" className="btn btn-secondary" onClick={clearFilters}>
            Wyczyść filtry
          </button>
        )}
      </form>

      {loading && !data && <Spinner label="Ładowanie modeli..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}

      {data && data.total === 0 && (
        <div className="empty-state">
          {filtersActive ? (
            <>
              <p>Brak wyników dla wybranych filtrów.</p>
              <button type="button" className="btn btn-secondary" onClick={clearFilters}>
                Wyczyść filtry
              </button>
            </>
          ) : (
            <>
              <p>Nie ma jeszcze żadnych modeli.</p>
              {isAdmin && (
                <Link to="/models/new" className="btn btn-primary">
                  Dodaj pierwszy model
                </Link>
              )}
            </>
          )}
        </div>
      )}

      {data && data.total > 0 && (
        <>
          <div className={`table-wrapper${loading ? " is-loading" : ""}`} aria-busy={loading}>
            <table>
              <thead>
                <tr>
                  <th>Nazwa</th>
                  <th>Framework</th>
                  <th>Zadanie</th>
                  <th>Wersja</th>
                  <th>Dokładność</th>
                  <th>Rozmiar</th>
                  <th>Plik</th>
                  <th>Status</th>
                  {isAdmin && <th>Akcje</th>}
                </tr>
              </thead>
              <tbody>
                {data.items.map((m) => (
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
                      {m.file_name ? (
                        <span className="file-cell">
                          {formatBytes(m.file_size)}
                          <DownloadButton modelId={m.id} className="link-button">
                            Pobierz
                          </DownloadButton>
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <StatusBadge status={m.status} />
                    </td>
                    {isAdmin && (
                      <td className="actions">
                        <Link to={`/models/${m.id}/edit`}>Edytuj</Link>
                        <button type="button" className="link-danger" onClick={() => setToDelete(m)}>
                          Usuń
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={data.page}
            pages={data.pages}
            total={data.total}
            pageSize={params.pageSize}
            onPageChange={(page) => updateParams({ page }, { replace: false })}
            onPageSizeChange={(pageSize) => updateParams({ pageSize, page: 1 })}
          />
        </>
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
