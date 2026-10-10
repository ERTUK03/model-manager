import { Link, useNavigate, useParams } from "react-router-dom";
import { createModel, getModel, updateModel } from "../api/models";
import ModelForm from "../components/ModelForm";
import { useFetch } from "../hooks/useFetch";
import { EMPTY_VALUES, toFormValues } from "../utils/mappers";

// Jeden ekran obsługuje dodawanie (/models/new) i edycję (/models/:id/edit)
export default function ModelFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { data: model, loading, error } = useFetch(
    () => (isEdit ? getModel(id) : Promise.resolve(null)),
    [id]
  );

  async function handleSubmit(payload) {
    const saved = isEdit ? await updateModel(id, payload) : await createModel(payload);
    navigate(`/models/${saved.id}`);
  }

  return (
    <section>
      <p>
        <Link to={isEdit ? `/models/${id}` : "/"}>← Anuluj</Link>
      </p>
      <h2>{isEdit ? "Edycja modelu" : "Nowy model"}</h2>

      {isEdit && loading && <p className="muted">Ładowanie...</p>}
      {isEdit && error && <p className="error">{error.message}</p>}

      {(!isEdit || model) && (
        <ModelForm
          initialValues={isEdit ? toFormValues(model) : EMPTY_VALUES}
          onSubmit={handleSubmit}
          submitLabel={isEdit ? "Zapisz zmiany" : "Dodaj model"}
        />
      )}
    </section>
  );
}
