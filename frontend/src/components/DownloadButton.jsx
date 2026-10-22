import { useState } from "react";
import { getDownloadInfo } from "../api/files";
import { useToast } from "../context/ToastContext";
import { startDownload } from "../utils/download";

// Pyta back-end o krótko ważny adres pliku i uruchamia pobieranie bezpośrednio z magazynu
export default function DownloadButton({ modelId, className = "btn btn-primary", children = "Pobierz plik" }) {
  const toast = useToast();
  const [busy, setBusy] = useState(false);

  async function handleClick() {
    setBusy(true);
    try {
      const { url } = await getDownloadInfo(modelId);
      startDownload(url);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <button type="button" className={className} onClick={handleClick} disabled={busy}>
      {busy ? "Przygotowywanie..." : children}
    </button>
  );
}
