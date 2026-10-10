import { useState } from "react";
import { FRAMEWORKS, STATUS_LABELS, STATUSES } from "../constants";
import { toPayload } from "../utils/mappers";

export default function ModelForm({ initialValues, onSubmit, submitLabel }) {
  const [values, setValues] = useState(initialValues);
  const [error, setError] = useState(null);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    try {
      await onSubmit(toPayload(values));
    } catch (err) {
      setError(err);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      {error && (
        <div className="error-box" role="alert">
          <strong>{error.message}</strong>
          {error.fieldErrors?.length > 0 && (
            <ul>
              {error.fieldErrors.map((e) => (
                <li key={e.field}>
                  {e.field.replace(/^body\./, "")}: {e.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="field">
        <label htmlFor="name">Nazwa</label>
        <input id="name" name="name" value={values.name} onChange={handleChange} />
      </div>

      <div className="field">
        <label htmlFor="description">Opis</label>
        <textarea id="description" name="description" rows={3} value={values.description} onChange={handleChange} />
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="framework">Framework</label>
          <select id="framework" name="framework" value={values.framework} onChange={handleChange}>
            <option value="">Wybierz...</option>
            {FRAMEWORKS.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="task">Zadanie</label>
          <input id="task" name="task" value={values.task} onChange={handleChange} />
        </div>
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="version">Wersja (X.Y.Z)</label>
          <input id="version" name="version" value={values.version} onChange={handleChange} />
        </div>
        <div className="field">
          <label htmlFor="accuracy">Dokładność (0–1)</label>
          <input id="accuracy" name="accuracy" value={values.accuracy} onChange={handleChange} />
        </div>
        <div className="field">
          <label htmlFor="size_mb">Rozmiar (MB)</label>
          <input id="size_mb" name="size_mb" value={values.size_mb} onChange={handleChange} />
        </div>
      </div>

      <div className="field">
        <label htmlFor="status">Status</label>
        <select id="status" name="status" value={values.status} onChange={handleChange}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
