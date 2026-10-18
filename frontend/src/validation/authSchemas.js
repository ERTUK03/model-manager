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

const PASSWORD_MESSAGE = "Hasło musi mieć co najmniej 8 znaków, w tym literę i cyfrę";

// Reguły takie same jak na serwerze (backend/app/schemas/user.py)
export const registerSchema = z
  .object({
    email: emailField,
    password: z
      .string()
      .min(8, PASSWORD_MESSAGE)
      .max(128, "Hasło może mieć maksymalnie 128 znaków")
      .refine((value) => /\p{L}/u.test(value) && /\p{Nd}/u.test(value), PASSWORD_MESSAGE),
    confirmPassword: z.string().min(1, "Powtórz hasło"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Hasła muszą być takie same",
    path: ["confirmPassword"],
  });
