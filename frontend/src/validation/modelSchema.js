import { z } from "zod";
import { FRAMEWORKS, STATUSES } from "../constants";

// Liczba nieujemna; przecinek lub kropka jako separator (np. 0.95 albo 0,95)
const NON_NEGATIVE_NUMBER = /^\d+([.,]\d+)?$/;
const toNumber = (value) => Number(value.replace(",", "."));

// Pole opcjonalne: puste jest poprawne, wypełnione musi być liczbą spełniającą warunek
const optionalNumber = (check, message) =>
  z
    .string()
    .trim()
    .refine((value) => value === "" || (NON_NEGATIVE_NUMBER.test(value) && check(toNumber(value))), message);

// Reguły odpowiadają walidacji po stronie serwera (backend/app/schemas/ml_model.py)
export const modelSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, "Nazwa jest wymagana (min. 2 znaki)")
    .max(100, "Nazwa może mieć maksymalnie 100 znaków"),
  description: z.string().trim().max(500, "Opis może mieć maksymalnie 500 znaków"),
  framework: z.string().refine((value) => FRAMEWORKS.includes(value), "Wybierz framework"),
  task: z
    .string()
    .trim()
    .min(2, "Zadanie jest wymagane (min. 2 znaki)")
    .max(50, "Zadanie może mieć maksymalnie 50 znaków"),
  version: z.string().trim().regex(/^\d+\.\d+\.\d+$/, "Podaj wersję w formacie X.Y.Z, np. 1.0.0"),
  accuracy: optionalNumber((n) => n <= 1, "Podaj liczbę od 0 do 1, np. 0.95"),
  size_mb: optionalNumber(() => true, "Podaj liczbę nieujemną, np. 12.5"),
  status: z.string().refine((value) => STATUSES.includes(value), "Wybierz status"),
});
