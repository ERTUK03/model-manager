import { Link } from "react-router-dom";

export default function ForbiddenPage() {
  return (
    <section>
      <h2>Brak uprawnień</h2>
      <p>Ta strona jest dostępna tylko dla administratorów.</p>
      <p>
        <Link to="/">Wróć do listy modeli</Link>
      </p>
    </section>
  );
}
