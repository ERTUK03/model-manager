import { z } from "zod";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Szczegółową walidację adresu wykonuje serwer; tu sprawdzamy podstawowy format
export const emailField = z
  .string()
  .trim()
  .min(1, "E-mail jest wymagany")
  .refine((value) => EMAIL_PATTERN.test(value), "Podaj poprawny adres e-mail");

export const loginSchema = z.object({
  email: emailField,
  password: z.string().min(1, "Hasło jest wymagane"),
});
