// Rozpoczyna pobieranie pliku z podanego adresu. Magazyn odsyła nagłówek Content-Disposition: attachment,
// więc przeglądarka zapisuje plik pod oryginalną nazwą i nie opuszcza aplikacji.
export function startDownload(url) {
  const link = document.createElement("a");
  link.href = url;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
}
