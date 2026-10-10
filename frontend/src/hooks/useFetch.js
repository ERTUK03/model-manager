import { useCallback, useEffect, useState } from "react";

// Pobiera dane i zarządza stanami: ładowanie, błąd, dane. reload() pobiera dane ponownie.
export function useFetch(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const load = useCallback(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    fetcher()
      .then((data) => !cancelled && setState({ data, loading: false, error: null }))
      .catch((error) => !cancelled && setState({ data: null, loading: false, error }));
    return () => {
      cancelled = true;
    };
  }, deps);

  useEffect(() => load(), [load]);

  return { ...state, reload: () => load() };
}
