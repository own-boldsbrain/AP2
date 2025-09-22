"""
PRE Orchestrator Agent

Este módulo contém a implementação do agente autônomo coordenador para orquestrar 
o processo PRE (captação → viabilidade → proposta) para o Yello Solar Hub.
"""

import os
import json
import uuid
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import nats
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pre_orchestrator")

# URLs base para os serviços
ORIGINATION_API_URL = os.getenv("ORIGINATION_API_URL", "http://origination_api:8000")
VIABILITY_SERVICE_URL = os.getenv("VIABILITY_SERVICE_URL", "http://viability_service:8010")
ANEEL_TARIFFS_URL = os.getenv("ANEEL_TARIFFS_URL", "http://aneel_tariffs:8011")
ANEEL_KPIS_URL = os.getenv("ANEEL_KPIS_URL", "http://aneel_kpis:8012")
ANEEL_UTILITIES_URL = os.getenv("ANEEL_UTILITIES_URL", "http://aneel_utilities:8013")
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")

# Valores padrão conservadores
DEFAULT_HSP = 5.0
DEFAULT_PR = 0.80
DEFAULT_LOSSES = 0.14
DEFAULT_TARIFF_CENTS_PER_KWH = 120

# Constantes para dimensionamento
TIER_FACTORS = {
    "T115": 1.15,
    "T130": 1.30,
    "T145": 1.45,
    "T160": 1.60
}

BAND_RANGES = {
    "XPP": (0, 0.5),
    "XS": (0.5, 3),
    "S": (3, 6),
    "M": (6, 12),
    "L": (12, 30),
    "XL": (30, 75),
    "XG": (75, 300),
    "XGG": (300, 1500)
}


class PREOrchestratorAgent:
    """Implementação do agente orquestrador de PRE."""
    
    def __init__(self):
        """Inicializa o agente."""
        self.http_client = httpx.AsyncClient(timeout=10.0)  # timeout de 10s
        self.nats_client = NATS()
        self.is_connected_nats = False
    
    async def connect_nats(self):
        """Conecta ao servidor NATS."""
        if not self.is_connected_nats:
            try:
                await self.nats_client.connect(NATS_URL)
                self.is_connected_nats = True
                logger.info("Conectado ao servidor NATS")
            except (ErrNoServers, ErrConnectionClosed) as e:
                logger.error(f"Erro ao conectar ao servidor NATS: {e}")
                raise
    
    async def disconnect_nats(self):
        """Desconecta do servidor NATS."""
        if self.is_connected_nats:
            await self.nats_client.close()
            self.is_connected_nats = False
            logger.info("Desconectado do servidor NATS")
    
    async def create_update_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria ou atualiza um lead no sistema.
        
        Args:
            lead_data: Dados do lead a ser criado/atualizado.
            
        Returns:
            Resposta da API com os dados do lead.
        """
        # Verificar consentimento LGPD
        if not lead_data.get("consent", False):
            raise ValueError("Consentimento LGPD é obrigatório.")
        
        # Normalizar dados
        if "cep" in lead_data:
            lead_data["cep"] = lead_data["cep"].strip().replace("-", "")
        
        if "uf" in lead_data:
            lead_data["uf"] = lead_data["uf"].strip().upper()
        
        # Chamar API para criar/atualizar lead
        url = f"{ORIGINATION_API_URL}/v1/leads"
        try:
            response = await self.http_client.post(url, json=lead_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao criar/atualizar lead: {e}")
            raise
    
    async def classify_consumer(self, lead_id: str, classification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifica o tipo de consumidor.
        
        Args:
            lead_id: ID do lead.
            classification_data: Dados de classificação.
            
        Returns:
            Resposta da API com os dados de classificação.
        """
        url = f"{ORIGINATION_API_URL}/v1/leads/{lead_id}/classify"
        try:
            response = await self.http_client.post(url, json=classification_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao classificar consumidor: {e}")
            raise
    
    async def select_modality(self, lead_id: str, modality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Seleciona a modalidade de geração.
        
        Args:
            lead_id: ID do lead.
            modality_data: Dados da modalidade.
            
        Returns:
            Resposta da API com os dados da modalidade.
        """
        url = f"{ORIGINATION_API_URL}/v1/leads/{lead_id}/modality"
        try:
            response = await self.http_client.post(url, json=modality_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao selecionar modalidade: {e}")
            raise
    
    async def calculate_viability(self, viability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula a viabilidade técnica do sistema solar.
        
        Args:
            viability_data: Dados para cálculo de viabilidade.
            
        Returns:
            Resposta da API com os dados de viabilidade.
        """
        url = f"{VIABILITY_SERVICE_URL}/tools/viability.compute"
        try:
            response = await self.http_client.post(url, json=viability_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao calcular viabilidade: {e}")
            raise
    
    async def get_tariff_profile(self, tariff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém o perfil tarifário.
        
        Args:
            tariff_data: Dados para obtenção do perfil tarifário.
            
        Returns:
            Perfil tarifário.
        """
        # Primeiro, buscar componentes tarifários
        url_components = f"{ANEEL_TARIFFS_URL}/tools/aneel.tariffs.components.fetch"
        try:
            response = await self.http_client.post(url_components, json=tariff_data)
            response.raise_for_status()
            components = response.json()
            
            # Em seguida, construir o perfil tarifário
            url_profile = f"{ANEEL_TARIFFS_URL}/tools/aneel.tariffs.profile.build"
            profile_response = await self.http_client.post(url_profile, json={"rows": components.get("rows", [])})
            profile_response.raise_for_status()
            return profile_response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao obter perfil tarifário: {e}")
            # Usar valores default em caso de erro
            return {"tariff_profile": {"cents_per_kwh": DEFAULT_TARIFF_CENTS_PER_KWH}}
    
    async def evaluate_economics(self, economics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia a viabilidade econômica do sistema solar.
        
        Args:
            economics_data: Dados para avaliação econômica.
            
        Returns:
            Resposta da API com os dados econômicos.
        """
        url = f"{VIABILITY_SERVICE_URL}/tools/economics.evaluate"
        try:
            response = await self.http_client.post(url, json=economics_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao avaliar economia: {e}")
            raise
    
    def size_system(self, sizing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dimensiona o sistema solar.
        
        Args:
            sizing_data: Dados para dimensionamento.
            
        Returns:
            Dados do dimensionamento.
        """
        consumo_anual = sizing_data.get("consumo_anual")
        hsp = sizing_data.get("hsp", DEFAULT_HSP)
        pr = sizing_data.get("pr", DEFAULT_PR)
        perdas = sizing_data.get("perdas", DEFAULT_LOSSES)
        fator_tier = sizing_data.get("fator_tier", TIER_FACTORS["T115"])
        
        # Cálculo do kWp
        kwp = (consumo_anual * fator_tier) / (hsp * 365 * pr * (1 - perdas))
        
        # Produção anual esperada
        expected_kwh_year = kwp * hsp * 365 * pr * (1 - perdas)
        
        # Determinar a banda com base no kWp
        band_code = None
        for band, (min_val, max_val) in BAND_RANGES.items():
            if min_val <= kwp < max_val:
                band_code = band
                break
        
        # Se o kWp for maior que o máximo da última banda, usar a última banda
        if band_code is None:
            if kwp >= BAND_RANGES["XGG"][1]:
                band_code = "XGG"
            else:
                band_code = "XPP"
        
        # Determinar o tier_code com base no fator_tier
        tier_code = None
        for tier, factor in TIER_FACTORS.items():
            if abs(factor - fator_tier) < 0.01:  # Comparação de floats com tolerância
                tier_code = tier
                break
        
        if tier_code is None:
            tier_code = "T115"  # Default
        
        return {
            "tier_code": tier_code,
            "band_code": band_code,
            "kwp": round(kwp, 2),
            "expected_kwh_year": round(expected_kwh_year, 0)
        }
    
    async def generate_recommendations(self, lead_id: str, reco_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera recomendações para o cliente.
        
        Args:
            lead_id: ID do lead.
            reco_data: Dados para geração de recomendações.
            
        Returns:
            Resposta da API com as recomendações.
        """
        url = f"{ORIGINATION_API_URL}/v1/leads/{lead_id}/recommendations"
        try:
            response = await self.http_client.post(url, json=reco_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            
            # Gerar recomendações localmente se a API falhar
            band_code = reco_data.get("band_code", "M")
            kwp = reco_data.get("kwp", 7.0)
            expected_kwh_year = reco_data.get("expected_kwh_year", 8000)
            
            # Criar ofertas Base/Plus/Pro com base no band_code e kwp
            offers = self._create_offers(band_code, kwp, expected_kwh_year)
            
            return {
                "offers": offers
            }
    
    def _create_offers(self, band_code: str, kwp: float, expected_kwh_year: float) -> List[Dict[str, Any]]:
        """
        Cria ofertas Base/Plus/Pro com base no band_code e kwp.
        
        Args:
            band_code: Código da banda.
            kwp: Potência do sistema em kWp.
            expected_kwh_year: Produção anual esperada em kWh.
            
        Returns:
            Lista de ofertas.
        """
        # Estimativa simples de CAPEX: R$ 7.000/kWp para Base, 8.000/kWp para Plus, 9.000/kWp para Pro
        capex_base = round(kwp * 7000, 2)
        capex_plus = round(kwp * 8000, 2)
        capex_pro = round(kwp * 9000, 2)
        
        # Estimativa de payback: 6 anos para Base, 5.5 para Plus, 5 para Pro
        payback_base = 6.0
        payback_plus = 5.5
        payback_pro = 5.0
        
        # Definir upsells com base no band_code
        upsells = self._get_upsells_by_band(band_code)
        
        offers = [
            {
                "sku": f"{band_code}-BASE",
                "title": f"Kit {band_code} Base",
                "capex_estimate": capex_base,
                "payback_estimate": payback_base,
                "upsell": upsells.get("base", ["BATERIA_STD", "DSM_TOU"])
            },
            {
                "sku": f"{band_code}-PLUS",
                "title": f"Kit {band_code} Plus",
                "capex_estimate": capex_plus,
                "payback_estimate": payback_plus,
                "upsell": upsells.get("plus", ["BATERIA_PRO", "MONITORING_BASIC"])
            },
            {
                "sku": f"{band_code}-PRO",
                "title": f"Kit {band_code} Pro",
                "capex_estimate": capex_pro,
                "payback_estimate": payback_pro,
                "upsell": upsells.get("pro", ["MONITORING_ADVANCED", "INSURANCE_PREMIUM"])
            }
        ]
        
        return offers
    
    def _get_upsells_by_band(self, band_code: str) -> Dict[str, List[str]]:
        """
        Define upsells com base no band_code.
        
        Args:
            band_code: Código da banda.
            
        Returns:
            Dicionário com upsells para cada tipo de oferta (base, plus, pro).
        """
        upsells = {
            "base": [],
            "plus": [],
            "pro": []
        }
        
        # Bands XS/S + perfil R-N → BATERIA_LIGHT, INSURANCE_BASIC, O&M_BASIC
        if band_code in ["XPP", "XS", "S"]:
            upsells["base"] = ["BATERIA_LIGHT", "INSURANCE_BASIC"]
            upsells["plus"] = ["BATERIA_LIGHT", "INSURANCE_BASIC", "O&M_BASIC"]
            upsells["pro"] = ["BATERIA_STD", "INSURANCE_STD", "O&M_BASIC"]
        
        # M/L → BATERIA_STD, DSM_TOU, INSURANCE_STD, O&M_STD
        elif band_code in ["M", "L"]:
            upsells["base"] = ["BATERIA_STD", "DSM_TOU"]
            upsells["plus"] = ["BATERIA_STD", "INSURANCE_STD", "O&M_STD"]
            upsells["pro"] = ["BATERIA_PRO", "INSURANCE_STD", "O&M_STD"]
        
        # XL/XG/XGG → O&M_PRO, INSURANCE_PREMIUM, MONITORING_ADVANCED
        elif band_code in ["XL", "XG", "XGG"]:
            upsells["base"] = ["O&M_STD", "INSURANCE_STD"]
            upsells["plus"] = ["O&M_PRO", "INSURANCE_PREMIUM"]
            upsells["pro"] = ["O&M_PRO", "INSURANCE_PREMIUM", "MONITORING_ADVANCED"]
        
        return upsells
    
    async def emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Emite um evento no sistema NATS.
        
        Args:
            event_type: Tipo de evento.
            payload: Payload do evento.
        """
        # Garantir conexão com NATS
        if not self.is_connected_nats:
            await self.connect_nats()
        
        # Adicionar trace_id ao payload se não existir
        if "trace_id" not in payload:
            payload["trace_id"] = str(uuid.uuid4())
        
        # Adicionar timestamp ao payload
        payload["timestamp"] = datetime.utcnow().isoformat()
        
        subject = f"ysh.origination.{event_type}"
        try:
            await self.nats_client.publish(subject, json.dumps(payload).encode())
            logger.info(f"Evento emitido: {subject}")
        except (ErrConnectionClosed, ErrTimeout) as e:
            logger.error(f"Erro ao emitir evento {subject}: {e}")
            # Tentar reconectar e reemitir
            await self.connect_nats()
            await self.nats_client.publish(subject, json.dumps(payload).encode())
    
    async def determine_modality(self, uc_type: str, has_roof: bool, multiple_ucs: bool) -> str:
        """
        Determina a modalidade de geração com base nos parâmetros.
        
        Args:
            uc_type: Tipo de unidade consumidora.
            has_roof: Indica se o cliente tem telhado adequado.
            multiple_ucs: Indica se o cliente tem múltiplas UCs.
            
        Returns:
            Modalidade de geração.
        """
        # Telhado adequado e UC única → AUTO_LOCAL
        if has_roof and not multiple_ucs and uc_type != "COND_MUC":
            return "AUTO_LOCAL"
        
        # Sem telhado/condomínio/comunhão → COMPARTILHADA ou MUC
        if not has_roof or uc_type == "COND_MUC":
            return "MUC" if uc_type == "COND_MUC" else "COMPARTILHADA"
        
        # Múltiplas UCs do mesmo titular → AUTO_REMOTO
        if multiple_ucs:
            return "AUTO_REMOTO"
        
        # Default
        return "AUTO_LOCAL"
    
    async def orchestrate_pre_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestra todo o processo PRE.
        
        Args:
            input_data: Dados de entrada para o processo.
            
        Returns:
            Resultado do processo.
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        telemetry = {"durations_ms": {}, "retries": {"http": 0, "events": 0}}
        logs = []
        errors = []
        
        # Inicializar dicionário para saída final
        final_output = {
            "trace_id": trace_id,
            "inputs_digest": "sha256-placeholder",  # Implementar hash real se necessário
            "final_bundle": {},
            "telemetry": telemetry,
            "logs": logs,
            "errors": errors
        }
        
        try:
            # Extrair dados de entrada
            lead_data = input_data.get("lead_data", {})
            consumption_data = input_data.get("consumption_data", {})
            preferences = input_data.get("preferences", {})
            
            # 1. Validate & Normalize
            capture_start = time.time()
            
            # Verificar consentimento LGPD
            if not lead_data.get("consent", False):
                raise ValueError("Consentimento LGPD é obrigatório.")
            
            # 2. Create/Upsert Lead
            lead_response = await self.create_update_lead(lead_data)
            lead_id = lead_response.get("lead_id", lead_data.get("lead_id"))
            
            logs.append({
                "level": "INFO",
                "at": datetime.utcnow().isoformat(),
                "msg": "lead.created"
            })
            
            # Emitir evento de lead capturado
            await self.emit_event("lead.captured.v1", {
                "lead_id": lead_id,
                "source": lead_data.get("source"),
                "consent": lead_data.get("consent")
            })
            
            telemetry["durations_ms"]["capture"] = round((time.time() - capture_start) * 1000, 2)
            
            # 3. Classify
            classification_data = {
                "tariff_group": input_data.get("tariff_group", "B1"),
                "consumer_class": input_data.get("consumer_class", "RESIDENCIAL"),
                "consumer_subclass": input_data.get("consumer_subclass", ""),
                "uc_type": input_data.get("uc_type", "RESIDENCIAL")
            }
            
            classification_response = await self.classify_consumer(lead_id, classification_data)
            
            # 4. Select Modality
            has_roof = preferences.get("has_roof", True)
            multiple_ucs = preferences.get("multiple_ucs", False)
            
            modality = await self.determine_modality(
                classification_data["uc_type"],
                has_roof,
                multiple_ucs
            )
            
            modality_data = {
                "generation_modality": modality,
                "principal_uc": preferences.get("principal_uc", ""),
                "members": preferences.get("members", [])
            }
            
            modality_response = await self.select_modality(lead_id, modality_data)
            
            # Emitir evento de modalidade selecionada
            await self.emit_event("generation.modality.selected.v1", {
                "lead_id": lead_id,
                "generation_modality": modality
            })
            
            # 5. Call Viability
            viability_start = time.time()
            
            lat = lead_data.get("lat")
            lon = lead_data.get("lon")
            
            if lat is None or lon is None:
                # Tentar extrair das preferências
                lat = preferences.get("lat")
                lon = preferences.get("lon")
            
            viability_data = {
                "lat": lat,
                "lon": lon,
                "tilt_deg": preferences.get("tilt_deg", 20),
                "azimuth_deg": preferences.get("azimuth_deg", 180),
                "mount_type": preferences.get("mount_type", "fixed"),
                "system_loss_fraction": preferences.get("system_loss_fraction", DEFAULT_LOSSES),
                "meteo_source": preferences.get("meteo_source", "NASA_POWER")
            }
            
            # Emitir evento de viabilidade solicitada
            await self.emit_event("viability.requested.v1", {
                "lead_id": lead_id,
                "viability_params": viability_data
            })
            
            viability_response = await self.calculate_viability(viability_data)
            
            logs.append({
                "level": "INFO",
                "at": datetime.utcnow().isoformat(),
                "msg": "viability.ok"
            })
            
            telemetry["durations_ms"]["viability"] = round((time.time() - viability_start) * 1000, 2)
            
            # Emitir evento de viabilidade concluída
            await self.emit_event("viability.completed.v1", {
                "lead_id": lead_id,
                "kwh_year_per_kwp": viability_response.get("kwh_year_per_kwp", 0),
                "pr": viability_response.get("pr", DEFAULT_PR)
            })
            
            # 6. Tariffs → Economics
            tariffs_start = time.time()
            
            tariff_data = {
                "sig_agente": preferences.get("sig_agente", ""),
                "inicio_vigencia": preferences.get("inicio_vigencia", "")
            }
            
            tariff_profile = await self.get_tariff_profile(tariff_data)
            
            telemetry["durations_ms"]["tariffs"] = round((time.time() - tariffs_start) * 1000, 2)
            
            economics_start = time.time()
            
            # Obter consumo anual
            consumo_anual = consumption_data.get("consumo_12m_kwh", 0)
            
            # Estimar kWp inicialmente para economics.evaluate
            hsp = viability_response.get("kwh_year_per_kwp", DEFAULT_HSP * 365) / 365
            pr = viability_response.get("pr", DEFAULT_PR)
            
            # Usar tier padrão T115 para estimativa inicial
            fator_tier = TIER_FACTORS["T115"]
            kwp_estimado = (consumo_anual * fator_tier) / (hsp * 365 * pr * (1 - DEFAULT_LOSSES))
            
            # Estimar produção anual
            kwh_year = kwp_estimado * hsp * 365 * pr * (1 - DEFAULT_LOSSES)
            
            # Estimar CAPEX e OPEX
            capex_estimado = kwp_estimado * 7000  # R$ 7.000/kWp (exemplo)
            opex_estimado = kwp_estimado * 100    # R$ 100/kWp/ano (exemplo)
            
            economics_data = {
                "kwh_year": kwh_year,
                "tariff_profile": tariff_profile.get("tariff_profile", {"cents_per_kwh": DEFAULT_TARIFF_CENTS_PER_KWH}),
                "capex": capex_estimado,
                "opex": opex_estimado
            }
            
            economics_response = await self.evaluate_economics(economics_data)
            
            logs.append({
                "level": "INFO",
                "at": datetime.utcnow().isoformat(),
                "msg": "economics.ok"
            })
            
            telemetry["durations_ms"]["economics"] = round((time.time() - economics_start) * 1000, 2)
            
            # 7. Sizing & Reco
            sizing_reco_start = time.time()
            
            # Obter o tier preferido
            preferred_tier = preferences.get("preferred_tier", "T115")
            fator_tier = TIER_FACTORS.get(preferred_tier, TIER_FACTORS["T115"])
            
            # Dimensionar o sistema
            sizing_data = {
                "consumo_anual": consumo_anual,
                "hsp": hsp,
                "pr": pr,
                "perdas": DEFAULT_LOSSES,
                "fator_tier": fator_tier
            }
            
            sizing_result = self.size_system(sizing_data)
            
            # Emitir evento de sistema dimensionado
            await self.emit_event("system.sized.v1", {
                "lead_id": lead_id,
                "kwp": sizing_result.get("kwp", 0),
                "tier_code": sizing_result.get("tier_code", "T115"),
                "band_code": sizing_result.get("band_code", "M"),
                "expected_kwh_year": sizing_result.get("expected_kwh_year", 0)
            })
            
            # Gerar recomendações
            reco_data = {
                "preferred_tier": preferred_tier,
                "tier_code": sizing_result.get("tier_code"),
                "band_code": sizing_result.get("band_code"),
                "kwp": sizing_result.get("kwp"),
                "expected_kwh_year": sizing_result.get("expected_kwh_year")
            }
            
            recommendations = await self.generate_recommendations(lead_id, reco_data)
            
            # Emitir evento de bundle de recomendações criado
            await self.emit_event("recommendation.bundle.created.v1", {
                "lead_id": lead_id,
                "offers_count": len(recommendations.get("offers", [])),
                "tier_code": sizing_result.get("tier_code"),
                "band_code": sizing_result.get("band_code")
            })
            
            logs.append({
                "level": "INFO",
                "at": datetime.utcnow().isoformat(),
                "msg": "bundle.created"
            })
            
            telemetry["durations_ms"]["sizing_reco"] = round((time.time() - sizing_reco_start) * 1000, 2)
            
            # 8. Montar JSON final
            final_bundle = {
                "lead_id": lead_id,
                "classification": {
                    "tariff_group": classification_data["tariff_group"],
                    "consumer_class": classification_data["consumer_class"],
                    "consumer_subclass": classification_data["consumer_subclass"],
                    "uc_type": classification_data["uc_type"],
                    "generation_modality": modality
                },
                "viability": {
                    "kwh_year_per_kwp": viability_response.get("kwh_year_per_kwp", 0),
                    "pr": viability_response.get("pr", DEFAULT_PR),
                    "mc_result": viability_response.get("mc_result", {})
                },
                "economics": {
                    "roi_pct": economics_response.get("roi_pct", 0),
                    "payback_years": economics_response.get("payback_years", 0),
                    "tir_pct": economics_response.get("tir_pct", 0)
                },
                "sizing": sizing_result,
                "offers": recommendations.get("offers", []),
                "events_emitted": [
                    "lead.captured.v1",
                    "generation.modality.selected.v1",
                    "viability.requested.v1",
                    "viability.completed.v1",
                    "system.sized.v1",
                    "recommendation.bundle.created.v1"
                ],
                "next_steps": [
                    "gerar_proposta_pdf",
                    "abrir_tarefa_homologacao",
                    "notificar_cliente"
                ]
            }
            
            final_output["final_bundle"] = final_bundle
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao orquestrar processo PRE: {error_msg}")
            errors.append({
                "level": "ERROR",
                "at": datetime.utcnow().isoformat(),
                "msg": f"Error: {error_msg}"
            })
        
        # Adicionar duração total
        telemetry["durations_ms"]["total"] = round((time.time() - start_time) * 1000, 2)
        
        return final_output
    
    async def close(self):
        """Fecha conexões."""
        await self.disconnect_nats()
        await self.http_client.aclose()


async def main():
    """Função principal para testes."""
    agent = PREOrchestratorAgent()
    
    # Exemplo de dados de entrada
    input_data = {
        "lead_data": {
            "lead_id": str(uuid.uuid4()),
            "source": "landing",
            "name": "João Silva",
            "email": "joao.silva@example.com",
            "phone": "21999999999",
            "consent": True,
            "cep": "22000-000",
            "uf": "RJ",
            "municipio": "Rio de Janeiro",
            "lat": -22.9,
            "lon": -43.2
        },
        "consumption_data": {
            "consumo_12m_kwh": 4000
        },
        "preferences": {
            "preferred_tier": "T130",
            "has_roof": True,
            "multiple_ucs": False,
            "tilt_deg": 20,
            "azimuth_deg": 180
        },
        "tariff_group": "B1",
        "consumer_class": "RESIDENCIAL",
        "uc_type": "RESIDENCIAL"
    }
    
    try:
        result = await agent.orchestrate_pre_process(input_data)
        print(json.dumps(result, indent=2))
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())