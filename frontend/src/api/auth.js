import { request } from "./client";

export const login = (email, password) =>
  request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }), auth: false });

export const getMe = () => request("/auth/me");
