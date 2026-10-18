import { request } from "./client";

export const getModelHistory = (id) => request(`/models/${id}/history`);

// Dziennik wszystkich zmian (tylko administrator): { items, total, page, page_size, pages }
export function getHistory({ action, page, pageSize }) {
  const query = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (action) query.set("action", action);
  return request(`/history?${query}`);
}
