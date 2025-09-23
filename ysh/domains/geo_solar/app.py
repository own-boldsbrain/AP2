from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from solposx import solar_position

app = FastAPI(title="YSH Solar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    return {"ok": True}


@app.get("/solpos")
def solpos(lat: float, lon: float, iso: str) -> dict[str, float | str]:
    """Calcula azimute e elevação solar para coordenadas e horário informados."""

    try:
        dt = datetime.fromisoformat(iso)
    except ValueError as exc:
        return {"error": f"Invalid ISO datetime: {exc}"}

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    solar = solar_position(latitude=lat, longitude=lon, timestamp=dt)
    return {
        "domain": "solar_geometry",
        "summary": "Efeméride instantânea calculada via solposx (SPA).",
        "timestamp_utc": dt.isoformat(),
        "azimuth_deg": solar.azimuth,
        "elevation_deg": solar.elevation,
    }
