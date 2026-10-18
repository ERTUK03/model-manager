import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { register as registerRequest } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { registerSchema } from "../validation/authSchemas";

const SERVER_FIELDS = ["email", "password"];

function FieldError({ error }) {
  if (!error) return null;
  return (
    <span className="field-error" role="alert">
      {error.message}
    </span>
  );
}

export default function RegisterPage() {
  const { user, login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [formError, setFormError] = useState(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
    mode: "onTouched",
  });

  if (user) return <Navigate to="/" replace />;

  async function submit(values) {
    setFormError(null);
    try {
      await registerRequest(values.email, values.password);
      await login(values.email, values.password);
      toast.success("Konto zostało utworzone.");
      navigate("/", { replace: true });
    } catch (err) {
      if (err.status === 409) {
        setError("email", { type: "server", message: err.message });
        return;
      }
      // Błędy walidacji z serwera (400) przypisujemy do pól formularza
      const fieldErrors = err.fieldErrors ?? [];
      fieldErrors.forEach(({ field, message }) => {
        const name = field.replace(/^body\./, "");
        if (SERVER_FIELDS.includes(name)) setError(name, { type: "server", message });
      });
      setFormError(fieldErrors.length > 0 ? "Serwer odrzucił dane. Popraw zaznaczone pola." : err.message);
    }
  }

  return (
    <section className="auth-card">
      <h2>Rejestracja</h2>
      <form className="form" onSubmit={handleSubmit(submit)} noValidate>
        {formError && (
          <div className="error-box" role="alert">
            {formError}
          </div>
        )}

        <div className="field">
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" autoComplete="email" aria-invalid={Boolean(errors.email)} {...register("email")} />
          <FieldError error={errors.email} />
        </div>

        <div className="field">
          <label htmlFor="password">Hasło</label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            aria-invalid={Boolean(errors.password)}
            {...register("password")}
          />
          <FieldError error={errors.password} />
        </div>

        <div className="field">
          <label htmlFor="confirmPassword">Powtórz hasło</label>
          <input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            aria-invalid={Boolean(errors.confirmPassword)}
            {...register("confirmPassword")}
          />
          <FieldError error={errors.confirmPassword} />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Tworzenie konta..." : "Utwórz konto"}
          </button>
        </div>
        <p className="auth-footer">
          Masz już konto? <Link to="/login">Zaloguj się</Link>
        </p>
      </form>
    </section>
  );
}
