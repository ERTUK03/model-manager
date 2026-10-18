import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { loginSchema } from "../validation/authSchemas";

export default function LoginPage() {
  const { user, login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [formError, setFormError] = useState(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
    mode: "onTouched",
  });

  const destination = location.state?.from?.pathname ?? "/";

  if (user) return <Navigate to="/" replace />;

  async function submit(values) {
    setFormError(null);
    try {
      await login(values.email, values.password);
      toast.success("Zalogowano.");
      navigate(destination, { replace: true });
    } catch (err) {
      setFormError(err.message);
    }
  }

  return (
    <section className="auth-card">
      <h2>Logowanie</h2>
      <form className="form" onSubmit={handleSubmit(submit)} noValidate>
        {formError && (
          <div className="error-box" role="alert">
            {formError}
          </div>
        )}

        <div className="field">
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" autoComplete="email" aria-invalid={Boolean(errors.email)} {...register("email")} />
          {errors.email && (
            <span className="field-error" role="alert">
              {errors.email.message}
            </span>
          )}
        </div>

        <div className="field">
          <label htmlFor="password">Hasło</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            aria-invalid={Boolean(errors.password)}
            {...register("password")}
          />
          {errors.password && (
            <span className="field-error" role="alert">
              {errors.password.message}
            </span>
          )}
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Logowanie..." : "Zaloguj się"}
          </button>
        </div>
      </form>
    </section>
  );
}
