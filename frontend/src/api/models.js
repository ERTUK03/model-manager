// Jedyne miejsce, które wie, skąd pochodzą dane.
// Przełączanie mock/API odbywa się zmienną środowiskową VITE_USE_MOCK.
const API_URL = import.meta.env.VITE_API_URL ?? "/api";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export async function getModels() {
  const url = USE_MOCK
    ? `${import.meta.env.BASE_URL}mock/models.json`
    : `${API_URL}/models`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Nie udało się pobrać danych (kod ${response.status})`);
  }

  const data = await response.json();
  // Back-end może zwracać tablicę lub obiekt z paginacją { items: [...] }
  return Array.isArray(data) ? data : data.items;
}
