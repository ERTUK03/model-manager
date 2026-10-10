import { Link, useNavigate, useParams } from "react-router-dom";
import { createModel, getModel, updateModel } from "../api/models";
import ErrorMessage from "../components/ErrorMessage";
import ModelForm from "../components/ModelForm";
import Spinner from "../components/Spinner";
import { useToast } from "../context/ToastContext";
import { useFetch } from "../hooks/useFetch";
import { EMPTY_VALUES, toFormValues } from "../utils/mappers";

// Jeden ekran obsługuje dodawanie (/models/new) i edycję (/models/:id/edit)
export default function ModelFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const toast = useToast();
  const { data: model, loading, error, reload } = useFetch(
    () => (isEdit ? getModel(id) : Promise.resolve(null)),
    [id]
  );

  async function handleSubmit(payload) {
    const saved = isEdit ? await updateModel(id, payload) : await createModel(payload);
    toast.success(isEdit ? "Zmiany zostały zapisane." : "Model został dodany.");
    navigate(`/models/${saved.id}`);
  }

  return (
    <section>
      <p>
        <Link to={isEdit ? `/models/${id}` : "/"}>← Anuluj</Link>
      </p>
      <h2>{isEdit ? "Edycja modelu" : "Nowy model"}</h2>

      {isEdit && loading && <Spinner label="Ładowanie modelu..." />}
      {isEdit && error && <ErrorMessage error={error} onRetry={error.status === 404 ? undefined : reload} />}

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
