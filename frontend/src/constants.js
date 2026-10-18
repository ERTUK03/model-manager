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
  status: "Status",
};

export const ACTION_LABELS = {
  created: "Utworzono",
  updated: "Zmieniono",
  deleted: "Usunięto",
};
