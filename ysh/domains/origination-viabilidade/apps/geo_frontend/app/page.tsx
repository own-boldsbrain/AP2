import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page">
      <section>
        <h1>Origination Geo Frontend</h1>
        <p>
          Explore photovoltaic origination sites with an interactive 3D Tiles viewer and solar illumination controls.
        </p>
      </section>
      <section>
        <Link className="link" href="/origination/tiles">
          Abrir visualizador 3D Tiles
        </Link>
      </section>
    </main>
  );
}
