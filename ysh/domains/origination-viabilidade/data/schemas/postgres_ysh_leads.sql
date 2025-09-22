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
