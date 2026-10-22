import { request } from "./client";

export function uploadModelFile(id, file) {
  const body = new FormData();
  body.append("file", file);
  return request(`/models/${id}/file`, { method: "POST", body });
}

export const deleteModelFile = (id) => request(`/models/${id}/file`, { method: "DELETE" });

// Zwraca { url, file_name, file_size, expires_in }. Adres jest krótko ważny i prowadzi bezpośrednio do magazynu
export const getDownloadInfo = (id) => request(`/models/${id}/download`);
