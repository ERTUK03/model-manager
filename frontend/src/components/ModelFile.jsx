import { useState } from "react";
import { deleteModelFile, uploadModelFile } from "../api/files";
import { ALLOWED_FILE_EXTENSIONS } from "../constants";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { validateModelFile } from "../utils/fileValidation";
import { formatBytes } from "../utils/format";
import ConfirmDialog from "./ConfirmDialog";
import DownloadButton from "./DownloadButton";

// Sekcja „Plik modelu” na stronie szczegółów: informacje o pliku i (dla administratora) wgrywanie oraz usuwanie
export default function ModelFile({ model, onChanged }) {
  const { isAdmin } = useAuth();
  const toast = useToast();
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [confirmRemove, setConfirmRemove] = useState(false);
  const [removing, setRemoving] = useState(false);
  const hasFile = Boolean(model.file_name);

  async function handleFileSelected(event) {
    const file = event.target.files?.[0];
    event.target.value = ""; // pozwala wybrać ten sam plik jeszcze raz
    if (!file) return;

    const problem = validateModelFile(file);
    if (problem) {
      setError(problem);
      return;
    }

    setError(null);
    setUploading(true);
    try {
      await uploadModelFile(model.id, file);
      toast.success(hasFile ? "Plik został zastąpiony." : "Plik został dodany.");
      onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleRemove() {
    setRemoving(true);
    try {
      await deleteModelFile(model.id);
      toast.success("Plik został usunięty.");
      setConfirmRemove(false);
      onChanged();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setRemoving(false);
    }
  }

  return (
    <section className="file-section">
      <h3>Plik modelu</h3>

      {hasFile ? (
        <dl className="details">
          <dt>Nazwa pliku</dt>
          <dd>{model.file_name}</dd>
          <dt>Rozmiar</dt>
          <dd>{formatBytes(model.file_size)}</dd>
          <dt>SHA-256</dt>
          <dd>
            <code className="hash">{model.file_sha256}</code>
          </dd>
        </dl>
      ) : (
        <p className="muted">Do tego modelu nie dodano jeszcze pliku.</p>
      )}

      {hasFile && (
        <p>
          <DownloadButton modelId={model.id} />
        </p>
      )}

      {isAdmin && (
        <div className="file-upload">
          <label htmlFor="model-file">{hasFile ? "Zastąp plik" : "Dodaj plik"}</label>
          <input
            id="model-file"
            type="file"
            accept={ALLOWED_FILE_EXTENSIONS.join(",")}
            disabled={uploading}
            onChange={handleFileSelected}
          />
          <p className="muted small">
            Dozwolone: {ALLOWED_FILE_EXTENSIONS.join(", ")}.{hasFile && " Wybranie nowego pliku zastąpi obecny."}
          </p>
          {uploading && (
            <p className="muted" role="status">
              Przesyłanie pliku...
            </p>
          )}
          {error && (
            <p className="field-error" role="alert">
              {error}
            </p>
          )}
          {hasFile && (
            <button type="button" className="btn btn-danger" onClick={() => setConfirmRemove(true)} disabled={uploading}>
              Usuń plik
            </button>
          )}
        </div>
      )}

      <ConfirmDialog
        open={confirmRemove}
        title="Usunąć plik?"
        message={`Plik „${model.file_name}” zostanie trwale usunięty z magazynu.`}
        confirmLabel="Usuń plik"
        busy={removing}
        onConfirm={handleRemove}
        onCancel={() => setConfirmRemove(false)}
      />
    </section>
  );
}
