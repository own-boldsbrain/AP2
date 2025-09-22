export const runtime = "edge";

export async function GET(_req: Request, ctx: { params: { path: string[] } }) {
  const path = ctx.params.path.join("/");
  const host = process.env.TILES_HOST;

  if (!host) {
    return new Response(JSON.stringify({ error: "Missing TILES_HOST environment variable" }), {
      status: 500,
      headers: { "content-type": "application/json" }
    });
  }

  const upstream = `https://${host}/${path}`;

  const response = await fetch(upstream, {
    headers: {
      "User-Agent": "YSH-TilesProxy"
    }
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") ?? "application/octet-stream",
      "cache-control": response.headers.get("cache-control") ?? "public, max-age=3600",
      "access-control-allow-origin": "*"
    }
  });
}
