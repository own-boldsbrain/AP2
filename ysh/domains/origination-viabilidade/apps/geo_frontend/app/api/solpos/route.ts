export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const lat = searchParams.get("lat");
    const lon = searchParams.get("lon");
    const iso = searchParams.get("iso");

    const base = process.env.SOLAR_API_BASE ?? "http://localhost:8000";
    const upstream = `${base.replace(/\/$/, "")}/solpos?lat=${lat ?? ""}&lon=${lon ?? ""}&iso=${encodeURIComponent(iso ?? "")}`;

    const response = await fetch(upstream, {
      method: "GET",
      redirect: "manual",
      headers: { accept: "application/json" }
    });

    if (response.status >= 300 && response.status < 400) {
      return new Response(
        JSON.stringify({ error: "Backend returned redirect. Serve FastAPI over HTTPS or disable redirects." }),
        {
          status: 502,
          headers: { "content-type": "application/json" }
        }
      );
    }

    const payload = await response.text();
    return new Response(payload, {
      status: response.status,
      headers: { "content-type": "application/json" }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: String(error) }), {
      status: 500,
      headers: { "content-type": "application/json" }
    });
  }
}
