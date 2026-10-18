import { toApiQuery } from "../utils/listParams";
import { request } from "./client";

// Zwraca stronę wyników: { items, total, page, page_size, pages }
export const getModels = (params) => request(`/models?${toApiQuery(params)}`);

export const getModel = (id) => request(`/models/${id}`);

export const createModel = (payload) => request("/models", { method: "POST", body: JSON.stringify(payload) });

export const updateModel = (id, payload) => request(`/models/${id}`, { method: "PUT", body: JSON.stringify(payload) });

export const deleteModel = (id) => request(`/models/${id}`, { method: "DELETE" });
