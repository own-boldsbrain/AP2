CREATE SCHEMA IF NOT EXISTS ysh;

CREATE TABLE IF NOT EXISTS ysh.leads (
  lead_id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  source TEXT,
  name TEXT,
  email TEXT,
  phone TEXT,
  cpf_cnpj TEXT,
  cep TEXT,
  uf TEXT,
  municipio TEXT,
  consent BOOLEAN NOT NULL,
  tariff_group TEXT,
  consumer_class TEXT,
  consumer_subclass TEXT,
  uc_type TEXT,
  generation_modality TEXT,
  ug_type TEXT,
  tier TEXT,
  region TEXT,
  status TEXT
);

CREATE TABLE IF NOT EXISTS ysh.lead_geo_kpis (
  composite_key TEXT PRIMARY KEY,
  lead_id UUID UNIQUE REFERENCES ysh.leads(lead_id),
  cpf TEXT NOT NULL,
  cep TEXT NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  properties JSONB DEFAULT '{}'::jsonb,
  kpis JSONB DEFAULT '{}'::jsonb,
  geojson JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS lead_geo_kpis_identity_idx
  ON ysh.lead_geo_kpis (cpf, cep, latitude, longitude);
