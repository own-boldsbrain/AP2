# Origination Geo Frontend

Frontend Next.js 15 para visualizar tiles 3D (OGC 3D Tiles) com iluminação solar dinâmica.

## Instalação

```bash
pnpm install
pnpm add three 3d-tiles-renderer
```

As dependências principais já estão declaradas em `package.json`. O comando `pnpm add` é necessário apenas se desejar atualizar manualmente `three` ou `3d-tiles-renderer`.

## Variáveis de ambiente

Crie um arquivo `.env.local` baseado em `.env.local.example`:

```env
NEXT_PUBLIC_TILESET_URL="https://YOUR_TILES_HOST/path/to/tileset.json"
SOLAR_API_BASE="https://localhost:8000"
TILES_HOST="cdn.example.com"
DEFAULT_LAT="-23.5505"
DEFAULT_LON="-46.6333"
DEFAULT_ISO="2025-09-21T13:00:00Z"
```

## Scripts

```bash
pnpm dev          # desenvolvimento http
pnpm dev:https    # desenvolvimento https experimental
pnpm build        # build de produção
pnpm start        # serve build de produção
```

## Rotas importantes

- `/origination/tiles`: viewer Three.js + 3D Tiles com painel de posição solar.
- `/origination/3d-tiles-proposal`: resumo da proposta de implantação.
- `/api/tiles/[...path]`: proxy para tiles (resolve CORS/assinaturas).
- `/api/solpos`: ponte para o serviço FastAPI `geo_solar`.

## Desenvolvimento do backend solar

O serviço FastAPI correspondente está em `ysh/domains/geo_solar/app.py`. Utilize `uvicorn` para executá-lo localmente.

## Conversão de dados em 3D Tiles

Use [`py3dtiles`](https://github.com/Oslandia/py3dtiles) para converter nuvens de pontos LAS/LAZ em tiles OGC 3D Tiles.

```bash
pip install py3dtiles
py3dtiles convert path/to/input.las ./tiles/out_city
```

Publique o diretório resultante (contendo `tileset.json`) em um CDN ou sirva via proxy `/api/tiles/...`.
