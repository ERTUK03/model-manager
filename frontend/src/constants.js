export const FRAMEWORKS = ["scikit-learn", "XGBoost", "PyTorch", "TensorFlow", "ONNX", "Other"];

export const STATUS_LABELS = {
  draft: "Szkic",
  published: "Opublikowany",
  archived: "Zarchiwizowany",
};

export const STATUSES = Object.keys(STATUS_LABELS);

export const ROLE_LABELS = {
  admin: "Administrator",
  user: "Użytkownik",
};

export const FIELD_LABELS = {
  name: "Nazwa",
  description: "Opis",
  framework: "Framework",
  task: "Zadanie",
  version: "Wersja",
  accuracy: "Dokładność",
  size_mb: "Rozmiar",
  file_name: "Plik",
  status: "Status",
};

export const ACTION_LABELS = {
  created: "Utworzono",
  updated: "Zmieniono",
  deleted: "Usunięto",
};

// Muszą odpowiadać ustawieniom back-endu (backend/app/services/file_service.py i MAX_UPLOAD_MB).
// Ostateczną kontrolę zawsze wykonuje serwer, tu sprawdzamy tylko po to, by szybciej pokazać błąd.
export const ALLOWED_FILE_EXTENSIONS = [".pkl", ".joblib", ".onnx", ".pt", ".pth", ".h5", ".safetensors"];
export const MAX_UPLOAD_MB = 200;

// Wersja aplikacji (skrót commita) wpisywana podczas budowania obrazu. Lokalnie: "dev"
export const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? "dev";
