CREATE TABLE IF NOT EXISTS ysh.reco_bands (
  code TEXT PRIMARY KEY, kwp_min NUMERIC, kwp_max NUMERIC
);
CREATE TABLE IF NOT EXISTS ysh.reco_tiers (
  code TEXT PRIMARY KEY, factor NUMERIC, label TEXT
);
CREATE TABLE IF NOT EXISTS ysh.recommendations (
  id UUID PRIMARY KEY,
  lead_id UUID NOT NULL REFERENCES ysh.leads(lead_id),
  ts TIMESTAMPTZ DEFAULT now(),
  tier_code TEXT REFERENCES ysh.reco_tiers(code),
  band_code TEXT REFERENCES ysh.reco_bands(code),
  kwp NUMERIC,
  expected_kwh_year NUMERIC,
  upsell JSONB,
  details JSONB
);
