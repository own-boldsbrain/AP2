"use client";

import { useEffect, useMemo, useState } from "react";
import ThreeTilesViewer from "../../../components/geo/ThreeTilesViewer";

type EnvDefaults = {
  lat: number;
  lon: number;
  iso: string;
};

function resolveEnvDefaults(): EnvDefaults {
  const fallbackLat = process.env.NEXT_PUBLIC_DEFAULT_LAT ?? process.env.DEFAULT_LAT ?? "-23.5505";
  const fallbackLon = process.env.NEXT_PUBLIC_DEFAULT_LON ?? process.env.DEFAULT_LON ?? "-46.6333";
  const fallbackIso = process.env.DEFAULT_ISO ?? new Date().toISOString();

  return {
    lat: Number(fallbackLat),
    lon: Number(fallbackLon),
    iso: fallbackIso
  };
}

export default function TilesPage() {
  const defaults = useMemo(resolveEnvDefaults, []);
  const [lat, setLat] = useState<number>(defaults.lat);
  const [lon, setLon] = useState<number>(defaults.lon);
  const [iso, setIso] = useState<string>(defaults.iso);

  useEffect(() => {
    if (Number.isNaN(lat)) {
      setLat(defaults.lat);
    }
    if (Number.isNaN(lon)) {
      setLon(defaults.lon);
    }
  }, [defaults.lat, defaults.lon, lat, lon]);

  const tilesetUrl = process.env.NEXT_PUBLIC_TILESET_URL;

  return (
    <main className="page">
      <section className="grid">
        <label>
          <span>Latitude</span>
          <input value={lat} onChange={(event) => setLat(Number(event.target.value))} />
        </label>
        <label>
          <span>Longitude</span>
          <input value={lon} onChange={(event) => setLon(Number(event.target.value))} />
        </label>
        <label>
          <span>ISO Datetime</span>
          <input value={iso} onChange={(event) => setIso(event.target.value)} />
        </label>
      </section>

      {tilesetUrl ? (
        <ThreeTilesViewer tilesetUrl={tilesetUrl} lat={lat} lon={lon} iso={iso} solarApiBase="/api/solpos" />
      ) : (
        <div className="viewer placeholder ysh-gradient-border">
          <p>Configure NEXT_PUBLIC_TILESET_URL no arquivo .env.local para carregar o tileset.</p>
        </div>
      )}
    </main>
  );
}
