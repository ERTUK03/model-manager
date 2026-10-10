import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { FRAMEWORKS, STATUS_LABELS, STATUSES } from "../constants";
import { toPayload } from "../utils/mappers";
import { modelSchema } from "../validation/modelSchema";

function Field({ id, label, error, children }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children}
      {error && (
        <span className="field-error" role="alert">
          {error.message}
        </span>
      )}
    </div>
  );
}

export default function ModelForm({ initialValues, onSubmit, submitLabel }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(modelSchema),
    defaultValues: initialValues,
    mode: "onTouched", // błędy pojawiają się po opuszczeniu pola, potem na bieżąco
  });
  const [formError, setFormError] = useState(null);

  async function submit(values) {
    setFormError(null);
    try {
      await onSubmit(toPayload(values));
    } catch (err) {
      // Błędy walidacji z serwera (400) przypisujemy do konkretnych pól
      const fieldErrors = err.fieldErrors ?? [];
      fieldErrors.forEach(({ field, message }) => {
        const name = field.replace(/^body\./, "");
        if (name in initialValues) setError(name, { type: "server", message });
      });
      setFormError(fieldErrors.length > 0 ? "Serwer odrzucił dane. Popraw zaznaczone pola." : err.message);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit(submit)} noValidate>
      {formError && (
        <div className="error-box" role="alert">
          {formError}
        </div>
      )}

      <Field id="name" label="Nazwa *" error={errors.name}>
        <input id="name" aria-invalid={Boolean(errors.name)} {...register("name")} />
      </Field>

      <Field id="description" label="Opis" error={errors.description}>
        <textarea id="description" rows={3} aria-invalid={Boolean(errors.description)} {...register("description")} />
      </Field>

      <div className="field-row">
        <Field id="framework" label="Framework *" error={errors.framework}>
          <select id="framework" aria-invalid={Boolean(errors.framework)} {...register("framework")}>
            <option value="">Wybierz...</option>
            {FRAMEWORKS.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </Field>
        <Field id="task" label="Zadanie *" error={errors.task}>
          <input id="task" aria-invalid={Boolean(errors.task)} {...register("task")} />
        </Field>
      </div>

      <div className="field-row">
        <Field id="version" label="Wersja (X.Y.Z) *" error={errors.version}>
          <input id="version" placeholder="1.0.0" aria-invalid={Boolean(errors.version)} {...register("version")} />
        </Field>
        <Field id="accuracy" label="Dokładność (0–1)" error={errors.accuracy}>
          <input id="accuracy" placeholder="0.95" aria-invalid={Boolean(errors.accuracy)} {...register("accuracy")} />
        </Field>
        <Field id="size_mb" label="Rozmiar (MB)" error={errors.size_mb}>
          <input id="size_mb" aria-invalid={Boolean(errors.size_mb)} {...register("size_mb")} />
        </Field>
      </div>

      <Field id="status" label="Status" error={errors.status}>
        <select id="status" aria-invalid={Boolean(errors.status)} {...register("status")}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </Field>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? "Zapisywanie..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
