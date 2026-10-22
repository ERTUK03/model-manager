import { ALLOWED_FILE_EXTENSIONS, MAX_UPLOAD_MB } from "../constants";

function extensionOf(name) {
  const dot = name.lastIndexOf(".");
  // Nazwa zaczynająca się od kropki (np. ".pkl") nie ma rozszerzenia, tak samo jak na serwerze
  return dot > 0 ? name.slice(dot).toLowerCase() : "";
}

// Zwraca komunikat o błędzie albo null, gdy plik wygląda poprawnie
export function validateModelFile(file) {
  if (!ALLOWED_FILE_EXTENSIONS.includes(extensionOf(file.name ?? ""))) {
    return `Niedozwolony typ pliku. Dozwolone rozszerzenia: ${ALLOWED_FILE_EXTENSIONS.join(", ")}`;
  }
  if (file.size === 0) return "Plik jest pusty";
  if (file.size > MAX_UPLOAD_MB * 1024 * 1024) return `Plik jest za duży (maksymalnie ${MAX_UPLOAD_MB} MB)`;
  return null;
}
