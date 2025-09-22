CREATE TABLE IF NOT EXISTS ysh.lead_features (
  lead_id UUID PRIMARY KEY REFERENCES ysh.leads(lead_id),
  score_engagement NUMERIC,
  score_finance NUMERIC,
  hsp NUMERIC,
  consumo_12m_kwh NUMERIC,
  load_profile TEXT,
  load_factor NUMERIC,
  tou_sensitivity JSONB,
  seasonal_index JSONB
);
