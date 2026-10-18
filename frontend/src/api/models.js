import { request } from "./client";

export async function getModels() {
  const data = await request("/models");
  // Back-end może zwracać tablicę lub obiekt z paginacją { items: [...] }
  return Array.isArray(data) ? data : data.items;
}

export const getModel = (id) => request(`/models/${id}`);

export const createModel = (payload) => request("/models", { method: "POST", body: JSON.stringify(payload) });

export const updateModel = (id, payload) => request(`/models/${id}`, { method: "PUT", body: JSON.stringify(payload) });

export const deleteModel = (id) => request(`/models/${id}`, { method: "DELETE" });
