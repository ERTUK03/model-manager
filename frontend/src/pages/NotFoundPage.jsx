import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <section>
      <h2>Nie znaleziono strony</h2>
      <p>
        <Link to="/">Wróć do listy modeli</Link>
      </p>
    </section>
  );
}
