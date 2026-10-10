import { ApiError, USE_MOCK, request } from "./client";

const MOCK_URL = `${import.meta.env.BASE_URL}mock/models.json`;

async function loadMock() {
  const response = await fetch(MOCK_URL);
  if (!response.ok) throw new ApiError("Nie udało się wczytać danych makietowych.");
  return response.json();
}

export async function getModels() {
  if (USE_MOCK) return loadMock();
  const data = await request("/models");
  // Back-end może zwracać tablicę lub obiekt z paginacją { items: [...] }
  return Array.isArray(data) ? data : data.items;
}

export async function getModel(id) {
  if (USE_MOCK) {
    const found = (await loadMock()).find((m) => String(m.id) === String(id));
    if (!found) throw new ApiError("Model nie istnieje", { status: 404 });
    return found;
  }
  return request(`/models/${id}`);
}

async function assertWritable() {
  if (USE_MOCK) {
    throw new ApiError("Tryb mock: zapis danych jest wyłączony. Ustaw VITE_USE_MOCK=false.");
  }
}

export async function createModel(payload) {
  await assertWritable();
  return request("/models", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateModel(id, payload) {
  await assertWritable();
  return request(`/models/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteModel(id) {
  await assertWritable();
  return request(`/models/${id}`, { method: "DELETE" });
}
