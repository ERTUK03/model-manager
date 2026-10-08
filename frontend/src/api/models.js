// Jedyne miejsce, które wie, skąd pochodzą dane.
// Teraz: plik JSON. Później: zapytanie do back-endu.
export async function getModels() {
  const response = await fetch("/mock/models.json");
  if (!response.ok) {
    throw new Error(`Nie udało się pobrać danych (kod ${response.status})`);
  }
  return response.json();
}
