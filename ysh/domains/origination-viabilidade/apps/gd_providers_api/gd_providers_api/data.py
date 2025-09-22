"""Static dataset describing MMGD provider submission portals."""

from __future__ import annotations

from typing import Dict

from .schemas import ProvidersDataset


RAW_DATA: Dict = {
    "api": "br.gd.providers",
    "version": "2025-09-20",
    "updated_at": "2025-09-20",
    "global": {
        "aneel_forms_page": "https://www.gov.br/aneel/pt-br/centrais-de-conteudos/formularios/geracao-distribuida",
        "legal_refs": ["REN ANEEL 1000/2021", "REN ANEEL 1059/2023", "Lei 14.300/2022"],
    },
    "providers": [
        {
            "id": "enel-rj",
            "name": "Enel Distribuição Rio",
            "group": "Enel",
            "states": ["RJ"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "portal": "https://www.eneldistribuicao.com.br/PortalGD/ENELRJ/Acessante/",
                    "basic_form": "https://www.eneldistribuicao.com.br/PortalGD/ENELRJ/Acessante/pages/formularioBasico.jsf",
                    "manual": "https://www.enel.com.br/content/dam/enel-br/one-hub-brasil---2018/corporativo-e-governo-/geracao_distribuida/AM037-20C-MANUAL-ACESSANTE-PORTAL-GERACAO-DISTRIBUIDA-20200923-FIM.pdf",
                },
                "requirements": {"login_required": False, "captcha": False},
            },
            "docs": {
                "howto": [
                    "https://www.enel.com.br/pt/Corporativo_e_Governo/Geracao_Distribuida.html"
                ]
            },
        },
        {
            "id": "enel-ce",
            "name": "Enel Distribuição Ceará",
            "group": "Enel",
            "states": ["CE"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "portal": "https://www.eneldistribuicao.com.br/PortalGD/ENELCE/Acessante/",
                    "basic_form": "https://www.eneldistribuicao.com.br/PortalGD/ENELCE/Acessante/pages/formularioBasico.jsf",
                },
                "requirements": {"login_required": False, "captcha": False},
            },
        },
        {
            "id": "light-rj",
            "name": "Light",
            "group": "Light",
            "states": ["RJ"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "gd_page": "https://www.light.com.br/SitePages/page-geracao-distribuida.aspx",
                    "portal_login": "https://agenciavirtual.light.com.br/Portal/inicio.aspx",
                    "downloads": "https://www.light.com.br/Documentos%20Compartilhados/Geracao-Distribuida-Arquivos-Relacionados/LIGHT_GERACAO_DISTRIBUIDA_site.pdf",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "neoenergia-elektro-sp",
            "name": "Neoenergia Elektro",
            "group": "Neoenergia",
            "states": ["SP", "MS"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "portal": "https://gdneoenergiaelektro.neoenergia.com/",
                    "help_flow": "https://www.neoenergia.com/web/sp/seu-negocio/geracao-distribuida",
                },
                "requirements": {
                    "login_required": True,
                    "captcha": True,
                    "captcha_vendor_hint": "BotDetect",
                },
            },
        },
        {
            "id": "neoenergia-coelba-ba",
            "name": "Neoenergia Coelba",
            "group": "Neoenergia",
            "states": ["BA"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "portal": "https://gdneoenergiacoelba.neoenergia.com/",
                    "signup": "https://gdneoenergiacoelba.neoenergia.com/cadastrarUsuario.jsf",
                },
                "requirements": {"login_required": True, "captcha": True},
            },
        },
        {
            "id": "neoenergia-cosern-rn",
            "name": "Neoenergia Cosern",
            "group": "Neoenergia",
            "states": ["RN"],
            "submission": {
                "type": "web_portal",
                "urls": {"portal": "https://gdneoenergiacosern.neoenergia.com/"},
                "requirements": {"login_required": True, "captcha": True},
            },
        },
        {
            "id": "neoenergia-pernambuco-pe",
            "name": "Neoenergia Pernambuco (CELPE)",
            "group": "Neoenergia",
            "states": ["PE"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "portal": "https://gdneoenergiapernambuco.neoenergia.com/",
                    "landing": "https://www.neoenergia.com/web/pernambuco/seu-negocio/geracao-distribuida",
                },
                "requirements": {"login_required": True, "captcha": True},
            },
        },
        {
            "id": "cpfl-sp",
            "name": "CPFL (Paulista/Piratininga e outras)",
            "group": "CPFL",
            "states": ["SP", "RS"],
            "submission": {
                "type": "web_portal_docs",
                "urls": {
                    "service_page": "https://www.cpfl.com.br/mini-e-microgeracao",
                    "norma_tecnica": "https://www.cpfl.com.br/sites/cpfl/files/2021-12/GED-15303.pdf",
                    "form_anexo_e_docx": "https://www.cpfl.com.br/sites/cpfl/files/2024-08/Formul%C3%A1rio%20%28Anexo%20E%20-%20GED%2015303%29.docx",
                    "form_anexo_f_xlsx": "https://www.cpfl.com.br/sites/cpfl/files/2025-01/Formul%C3%A1rio%20Anexo%20F%20-%20GED%2015303.xlsx",
                    "cartilha": "https://www.cpfl.com.br/sites/cpfl/files/2024-10/CARTILHA%20GD%20CPFL.pdf",
                },
                "requirements": {"login_required": False, "captcha": False},
            },
        },
        {
            "id": "cemig-mg",
            "name": "Cemig",
            "group": "Cemig",
            "states": ["MG"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "manual_gd": "https://www.cemig.com.br/manual-de-geracao-distribuida/",
                    "portal_login": "https://atende.cemig.com.br/Login",
                    "norma_nd530_pdf": "https://www.cemig.com.br/wp-content/uploads/2020/07/ND.5.30.pdf",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "celesc-sc",
            "name": "Celesc",
            "group": "Celesc",
            "states": ["SC"],
            "submission": {
                "type": "web_portal_docs",
                "urls": {
                    "service_page": "https://www.celesc.com.br/conexao-de-micro-ou-minigerador",
                    "instruicao_i4320004_pdf": "https://www.celesc.com.br/arquivos/normas-tecnicas/conexao-centrais-geradoras/conexao-micro-mini-geradores-out2020.pdf",
                    "guia_portal_tecnico_pdf": "https://www.celesc.com.br/images/central-ajuda/micro-mini-geracao/Guia-cadastro-de-projetos-Portal-Tecnico.pdf",
                },
                "requirements": {"login_required": False, "captcha": False},
            },
        },
        {
            "id": "edp-es-sp",
            "name": "EDP (ES e SP)",
            "group": "EDP",
            "states": ["ES", "SP"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://www.edp.com.br/micro-e-mini-geracao/",
                    "form_mmgd": "https://www.edp.com.br/micro-e-mini-geracao/formulario-mmgd-solicitacao-de-acesso",
                    "agencia_login": "https://www.edponline.com.br/para-sua-casa/login",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "equatorial-go",
            "name": "Equatorial Goiás",
            "group": "Equatorial",
            "states": ["GO"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://go.equatorialenergia.com.br/sua-conta/geracao-distribuida/",
                    "parecer_de_acesso": "https://go.equatorialenergia.com.br/sua-conta/geracao-distribuida/parecer-de-acesso/",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "equatorial-pi",
            "name": "Equatorial Piauí",
            "group": "Equatorial",
            "states": ["PI"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://pi.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/",
                    "parecer_de_acesso": "https://pi.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/parecer-de-acesso/",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "equatorial-ma",
            "name": "Equatorial Maranhão",
            "group": "Equatorial",
            "states": ["MA"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://ma.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/",
                    "parecer_de_acesso": "https://ma.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/parecer-de-acesso/",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "equatorial-pa",
            "name": "Equatorial Pará",
            "group": "Equatorial",
            "states": ["PA"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://pa.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/"
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "equatorial-ap",
            "name": "Equatorial Amapá (CEA)",
            "group": "Equatorial",
            "states": ["AP"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://ap.equatorialenergia.com.br/sua-conta/mini-e-micro-geracao/"
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "energisa-group",
            "name": "Energisa (Grupo – múltiplos estados)",
            "group": "Energisa",
            "states": ["AC", "RO", "TO", "PB", "SE", "MT", "MS", "MG", "RJ", "SP", "PR"],
            "submission": {
                "type": "web_portal_docs",
                "urls": {
                    "landing": "https://www.energisa.com.br/para-sua-casa/servicos/outros-servicos/geracao-distribuida",
                    "faq_docs": "https://ajuda.energisa.com.br/categoria/micro-minigeracao/",
                    "ndu_015_pdf": "https://www.energisa.com.br/sites/energisa/files/media/documents/2025-02/NDU%20015%20-%20Crit%C3%A9rios%20para%20a%20Conex%C3%A3o%20em%20M%C3%A9dia%20Tens%C3%A3o%20de%20Acessantes%20de%20Gera%C3%A7%C3%A3o%20Distribu%C3%ADda%20ao%20Sistema%20de%20Distribui%C3%A7%C3%A3o_.pdf",
                },
                "requirements": {"login_required": "case", "captcha": False},
                "notes": "Formulários oficiais ficam nos anexos das NDU-013/015; checar por distribuidora do grupo.",
            },
        },
        {
            "id": "copel-pr",
            "name": "Copel",
            "group": "Copel",
            "states": ["PR"],
            "submission": {
                "type": "web_portal_docs",
                "urls": {
                    "vistoria_info": "https://www.copel.com/site/fornecedores-e-parceiros/geracao-distribuida/",
                    "vistoria_news": "https://www.parana.pr.gov.br/aen/Noticia/Copel-oferece-vistoria-virtual-para-ligacoes-de-imoveis-novos",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "amazonas-energia",
            "name": "Amazonas Energia",
            "group": "Amazonas Energia",
            "states": ["AM"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "landing": "https://website.amazonasenergia.com/informacoes/micro-minigeracao-distribuida/",
                    "proger_login": "https://proger.amazonasenergia.com/",
                    "manual_proger": "https://website.amazonasenergia.com/wp-content/uploads/2022/05/Manual-Sistema-Amazonas-Energia-vers-02.pdf",
                },
                "requirements": {"login_required": True, "captcha": False},
            },
        },
        {
            "id": "roraima-energia",
            "name": "Roraima Energia",
            "group": "Roraima Energia",
            "states": ["RR"],
            "submission": {
                "type": "web_portal",
                "urls": {
                    "conexao_facil": "https://conexaofacil.roraimaenergia.com.br/",
                    "mmgd_page": "https://www.roraimaenergia.com.br/nossos-servicos/micro-minigeracao-distribuida/",
                    "proger_login": "https://proger.roraimaenergia.com.br/",
                },
                "requirements": {"login_required": True, "captcha": False},
                "notes": "Desde 11/11/2024, microgeração via Conexão Fácil (GDIS).",
            },
        },
    ],
}


def _validate_dataset(raw: Dict) -> ProvidersDataset:
    """Validate the raw data using Pydantic, supporting multiple versions."""

    if hasattr(ProvidersDataset, "model_validate"):
        return ProvidersDataset.model_validate(raw)  # type: ignore[attr-defined]
    return ProvidersDataset.parse_obj(raw)  # pragma: no cover


DATASET: ProvidersDataset = _validate_dataset(RAW_DATA)
PROVIDERS_BY_ID = {provider.id: provider for provider in DATASET.providers}
