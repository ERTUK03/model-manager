import { request } from "./client";

export function uploadModelFile(id, file) {
  const body = new FormData();
  body.append("file", file);
  return request(`/models/${id}/file`, { method: "POST", body });
}

export const deleteModelFile = (id) => request(`/models/${id}/file`, { method: "DELETE" });
