export default function ProposalPage() {
  return (
    <main className="page">
      <article className="proposal">
        <header>
          <h1>Incorporação 3D Tiles (OGC) · YSH</h1>
          <p>Next 15 + Three.js + 3D Tiles + solposx + FastAPI</p>
        </header>
        <section>
          <p>
            Streaming 3D geoespacial com TilesRenderer (Three.js), tiles via CDN/Proxy e iluminação solar (solposx).
          </p>
          <ul>
            <li>Viewer: <code>components/geo/ThreeTilesViewer.tsx</code></li>
            <li>Página: <code>/origination/tiles</code></li>
            <li>Proxy: <code>/api/tiles/[...path]</code></li>
            <li>Solar API: <code>domains/geo_solar/app.py</code></li>
          </ul>
        </section>
      </article>
    </main>
  );
}
