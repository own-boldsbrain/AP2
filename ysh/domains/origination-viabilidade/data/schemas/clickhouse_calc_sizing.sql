CREATE TABLE IF NOT EXISTS calc.sizing
(
  lead_id UUID,
  ts DateTime,
  kwp Float64,
  kwh_year Float64,
  pr Float64,
  losses_map String,
  capex_kit Float64,
  capex_mao_obra Float64,
  capex_projeto Float64,
  capex_homologacao Float64,
  capex_comissao Float64,
  capex_logistica Float64,
  capex_contingencia Float64
)
ENGINE = MergeTree
ORDER BY (lead_id, ts);
