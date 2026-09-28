"""Tools do MCP da Google Ads API.

Leitura: contas, campanhas, anúncios, palavras-chave e GAQL livre.
Escrita: criação de anúncio de pesquisa responsivo, status de anúncio e
campanha, e orçamento diário. As tools de escrita só funcionam com
GOOGLE_ADS_MCP_ALLOW_WRITES=1.
"""

import json
from typing import Any, Optional

from google_ads_mcp.client import (
    GoogleAdsClient,
    micros_to_units,
    normalize_customer_id,
)

_client = GoogleAdsClient()

_MAX_HEADLINE = 30
_MAX_DESCRIPTION = 90
_MAX_PATH = 15


def _dump(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str, indent=2)


def _dig(row: dict[str, Any], path: str) -> Any:
    """Lê um caminho aninhado da resposta REST, ex: 'adGroupAd.ad.id'."""
    current: Any = row
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _metrics(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics") or {}
    cost = micros_to_units(metrics.get("costMicros"))
    clicks = int(metrics.get("clicks") or 0)
    impressions = int(metrics.get("impressions") or 0)
    return {
        "impressoes": impressions,
        "cliques": clicks,
        "ctr": round(clicks / impressions * 100, 2) if impressions else 0.0,
        "custo": cost,
        "cpc_medio": round(cost / clicks, 2) if cost and clicks else None,
        "conversoes": float(metrics.get("conversions") or 0),
    }


# ---------------------------------------------------------------- leitura

async def list_accessible_customers() -> str:
    """Lista as contas do Google Ads que o refresh token configurado alcança.

    Use como primeiro diagnóstico: se a conta que você quer operar não
    aparecer aqui nem em list_client_accounts, o acesso não existe."""
    payload = await _client.request("GET", "customers:listAccessibleCustomers")
    resource_names = payload.get("resourceNames", [])
    return _dump(
        {
            "total": len(resource_names),
            "contas": [name.split("/")[-1] for name in resource_names],
        }
    )


async def list_client_accounts(manager_customer_id: Optional[str] = None) -> str:
    """Lista as contas filhas penduradas numa conta administradora (MCC).

    Args:
        manager_customer_id: ID da MCC. Se omitido, usa o
            GOOGLE_ADS_LOGIN_CUSTOMER_ID do ambiente."""
    manager = manager_customer_id or _client.config()["login_customer_id"]
    query = """
        SELECT customer_client.id,
               customer_client.descriptive_name,
               customer_client.currency_code,
               customer_client.time_zone,
               customer_client.manager,
               customer_client.status,
               customer_client.level
        FROM customer_client
        WHERE customer_client.status != 'CLOSED'
    """
    rows = await _client.search(manager, query)
    contas = [
        {
            "id": _dig(row, "customerClient.id"),
            "nome": _dig(row, "customerClient.descriptiveName"),
            "moeda": _dig(row, "customerClient.currencyCode"),
            "fuso": _dig(row, "customerClient.timeZone"),
            "administradora": _dig(row, "customerClient.manager"),
            "status": _dig(row, "customerClient.status"),
            "nivel": _dig(row, "customerClient.level"),
        }
        for row in rows
    ]
    return _dump({"mcc": manager, "total": len(contas), "contas": contas})


async def run_gaql(customer_id: str, query: str, page_size: int = 200) -> str:
    """Roda uma consulta GAQL livre numa conta e devolve as linhas cruas.

    Saída de emergência para o que as outras tools não cobrem.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        query: consulta GAQL completa, começando por SELECT.
        page_size: linhas por página (máximo 10000)."""
    rows = await _client.search(customer_id, query, page_size=page_size)
    return _dump({"total": len(rows), "linhas": rows})


async def list_campaigns(
    customer_id: str,
    include_metrics: bool = True,
    date_range: str = "LAST_30_DAYS",
) -> str:
    """Lista as campanhas de uma conta, com métricas do período.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        include_metrics: quando falso, lista também campanhas sem entrega
            no período, porque a consulta não segmenta por data.
        date_range: literal de data do GAQL, ex: LAST_7_DAYS, LAST_30_DAYS,
            THIS_MONTH, LAST_MONTH."""
    fields = """
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        campaign_budget.id,
        campaign_budget.amount_micros
    """
    if include_metrics:
        query = f"""
            SELECT {fields},
                   metrics.impressions, metrics.clicks,
                   metrics.cost_micros, metrics.conversions
            FROM campaign
            WHERE campaign.status != 'REMOVED'
              AND segments.date DURING {date_range}
        """
    else:
        query = f"""
            SELECT {fields}
            FROM campaign
            WHERE campaign.status != 'REMOVED'
        """

    rows = await _client.search(customer_id, query)
    campanhas = []
    for row in rows:
        item = {
            "id": _dig(row, "campaign.id"),
            "nome": _dig(row, "campaign.name"),
            "status": _dig(row, "campaign.status"),
            "canal": _dig(row, "campaign.advertisingChannelType"),
            "estrategia_lance": _dig(row, "campaign.biddingStrategyType"),
            "orcamento_id": _dig(row, "campaignBudget.id"),
            "orcamento_diario": micros_to_units(
                _dig(row, "campaignBudget.amountMicros")
            ),
        }
        if include_metrics:
            item["metricas"] = _metrics(row)
        campanhas.append(item)

    return _dump(
        {
            "conta": normalize_customer_id(customer_id),
            "periodo": date_range if include_metrics else None,
            "total": len(campanhas),
            "campanhas": campanhas,
        }
    )


async def list_ads(
    customer_id: str,
    campaign_id: Optional[str] = None,
    only_disapproved: bool = False,
) -> str:
    """Lista anúncios com URL final e situação de política.

    É a tool para diagnosticar reprovação por destino que não funciona:
    devolve a URL final de cada anúncio e os tópicos de política violados.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        campaign_id: filtra por uma campanha.
        only_disapproved: quando verdadeiro, traz só os reprovados."""
    conditions = ["ad_group_ad.status != 'REMOVED'"]
    if campaign_id:
        conditions.append(f"campaign.id = {int(campaign_id)}")
    if only_disapproved:
        conditions.append("ad_group_ad.policy_summary.approval_status = 'DISAPPROVED'")

    query = f"""
        SELECT ad_group_ad.ad.id,
               ad_group_ad.ad.name,
               ad_group_ad.ad.type,
               ad_group_ad.ad.final_urls,
               ad_group_ad.status,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.policy_summary.policy_topic_entries,
               ad_group.id,
               ad_group.name,
               campaign.id,
               campaign.name
        FROM ad_group_ad
        WHERE {' AND '.join(conditions)}
    """

    rows = await _client.search(customer_id, query)
    anuncios = []
    for row in rows:
        topicos = _dig(row, "adGroupAd.policySummary.policyTopicEntries") or []
        anuncios.append(
            {
                "anuncio_id": _dig(row, "adGroupAd.ad.id"),
                "tipo": _dig(row, "adGroupAd.ad.type"),
                "status": _dig(row, "adGroupAd.status"),
                "urls_finais": _dig(row, "adGroupAd.ad.finalUrls") or [],
                "aprovacao": _dig(row, "adGroupAd.policySummary.approvalStatus"),
                "revisao": _dig(row, "adGroupAd.policySummary.reviewStatus"),
                "politicas": [
                    {"topico": t.get("topic"), "tipo": t.get("type")} for t in topicos
                ],
                "grupo_anuncio_id": _dig(row, "adGroup.id"),
                "grupo_anuncio": _dig(row, "adGroup.name"),
                "campanha_id": _dig(row, "campaign.id"),
                "campanha": _dig(row, "campaign.name"),
            }
        )

    return _dump(
        {
            "conta": normalize_customer_id(customer_id),
            "total": len(anuncios),
            "anuncios": anuncios,
        }
    )


async def list_keywords(
    customer_id: str,
    campaign_id: Optional[str] = None,
    date_range: str = "LAST_30_DAYS",
) -> str:
    """Lista palavras-chave com desempenho no período.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        campaign_id: filtra por uma campanha.
        date_range: literal de data do GAQL, ex: LAST_30_DAYS."""
    conditions = [
        "ad_group_criterion.status != 'REMOVED'",
        f"segments.date DURING {date_range}",
    ]
    if campaign_id:
        conditions.append(f"campaign.id = {int(campaign_id)}")

    query = f"""
        SELECT ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type,
               ad_group_criterion.status,
               ad_group.name,
               campaign.id,
               campaign.name,
               metrics.impressions, metrics.clicks,
               metrics.cost_micros, metrics.conversions
        FROM keyword_view
        WHERE {' AND '.join(conditions)}
    """

    rows = await _client.search(customer_id, query)
    palavras = [
        {
            "termo": _dig(row, "adGroupCriterion.keyword.text"),
            "correspondencia": _dig(row, "adGroupCriterion.keyword.matchType"),
            "status": _dig(row, "adGroupCriterion.status"),
            "grupo_anuncio": _dig(row, "adGroup.name"),
            "campanha": _dig(row, "campaign.name"),
            "metricas": _metrics(row),
        }
        for row in rows
    ]
    palavras.sort(key=lambda p: p["metricas"]["cliques"], reverse=True)

    return _dump(
        {
            "conta": normalize_customer_id(customer_id),
            "periodo": date_range,
            "total": len(palavras),
            "palavras": palavras,
        }
    )


# ---------------------------------------------------------------- escrita

async def create_responsive_search_ad(
    customer_id: str,
    ad_group_id: str,
    final_url: str,
    headlines: list[str],
    descriptions: list[str],
    path1: Optional[str] = None,
    path2: Optional[str] = None,
    status: str = "PAUSED",
    validate_only: bool = False,
) -> str:
    """Cria um anúncio de pesquisa responsivo num grupo de anúncios.

    A API não permite editar a URL final de um anúncio existente. Para
    corrigir destino quebrado, crie o anúncio novo com esta tool e pause o
    antigo com set_ad_status.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        ad_group_id: ID do grupo de anúncios que recebe o anúncio.
        final_url: URL de destino, precisa responder 200 ao AdsBot.
        headlines: 3 a 15 títulos, até 30 caracteres cada.
        descriptions: 2 a 4 descrições, até 90 caracteres cada.
        path1: primeiro caminho do URL de exibição, até 15 caracteres.
        path2: segundo caminho do URL de exibição, até 15 caracteres.
        status: PAUSED (padrão) ou ENABLED.
        validate_only: quando verdadeiro, só valida e não cria nada."""
    _client.require_writes()

    problemas = []
    if not 3 <= len(headlines) <= 15:
        problemas.append(f"títulos: {len(headlines)}, precisa de 3 a 15")
    if not 2 <= len(descriptions) <= 4:
        problemas.append(f"descrições: {len(descriptions)}, precisa de 2 a 4")
    for texto in headlines:
        if len(texto) > _MAX_HEADLINE:
            problemas.append(f"título acima de {_MAX_HEADLINE} caracteres: {texto!r}")
    for texto in descriptions:
        if len(texto) > _MAX_DESCRIPTION:
            problemas.append(
                f"descrição acima de {_MAX_DESCRIPTION} caracteres: {texto!r}"
            )
    for caminho in (path1, path2):
        if caminho and len(caminho) > _MAX_PATH:
            problemas.append(f"caminho acima de {_MAX_PATH} caracteres: {caminho!r}")
    if status not in ("PAUSED", "ENABLED"):
        problemas.append(f"status inválido: {status!r}, use PAUSED ou ENABLED")
    if problemas:
        return _dump({"criado": False, "erros": problemas})

    cid = normalize_customer_id(customer_id)
    responsive: dict[str, Any] = {
        "headlines": [{"text": t} for t in headlines],
        "descriptions": [{"text": t} for t in descriptions],
    }
    if path1:
        responsive["path1"] = path1
    if path2:
        responsive["path2"] = path2

    operation = {
        "create": {
            "adGroup": f"customers/{cid}/adGroups/{int(ad_group_id)}",
            "status": status,
            "ad": {"finalUrls": [final_url], "responsiveSearchAd": responsive},
        }
    }
    result = await _client.mutate(
        cid, "adGroupAds", [operation], validate_only=validate_only
    )
    return _dump({"criado": not validate_only, "validacao": validate_only, "resposta": result})


async def set_ad_status(
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    status: str,
    validate_only: bool = False,
) -> str:
    """Pausa, ativa ou remove um anúncio.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        ad_group_id: ID do grupo de anúncios do anúncio.
        ad_id: ID do anúncio.
        status: ENABLED, PAUSED ou REMOVED.
        validate_only: quando verdadeiro, só valida."""
    _client.require_writes()
    if status not in ("ENABLED", "PAUSED", "REMOVED"):
        return _dump({"alterado": False, "erro": f"status inválido: {status!r}"})

    cid = normalize_customer_id(customer_id)
    resource = f"customers/{cid}/adGroupAds/{int(ad_group_id)}~{int(ad_id)}"
    operation = {
        "update": {"resourceName": resource, "status": status},
        "updateMask": "status",
    }
    result = await _client.mutate(
        cid, "adGroupAds", [operation], validate_only=validate_only
    )
    return _dump({"alterado": not validate_only, "recurso": resource, "resposta": result})


async def set_campaign_status(
    customer_id: str,
    campaign_id: str,
    status: str,
    validate_only: bool = False,
) -> str:
    """Pausa, ativa ou remove uma campanha.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        campaign_id: ID da campanha.
        status: ENABLED, PAUSED ou REMOVED.
        validate_only: quando verdadeiro, só valida."""
    _client.require_writes()
    if status not in ("ENABLED", "PAUSED", "REMOVED"):
        return _dump({"alterado": False, "erro": f"status inválido: {status!r}"})

    cid = normalize_customer_id(customer_id)
    resource = f"customers/{cid}/campaigns/{int(campaign_id)}"
    operation = {
        "update": {"resourceName": resource, "status": status},
        "updateMask": "status",
    }
    result = await _client.mutate(
        cid, "campaigns", [operation], validate_only=validate_only
    )
    return _dump({"alterado": not validate_only, "recurso": resource, "resposta": result})


async def set_campaign_budget(
    customer_id: str,
    campaign_id: str,
    daily_amount: float,
    validate_only: bool = False,
) -> str:
    """Altera o orçamento diário da campanha, na moeda da conta.

    Args:
        customer_id: ID da conta, com ou sem hífens.
        campaign_id: ID da campanha cujo orçamento será alterado.
        daily_amount: novo valor diário, ex: 25.50.
        validate_only: quando verdadeiro, só valida."""
    _client.require_writes()
    cid = normalize_customer_id(customer_id)

    rows = await _client.search(
        cid,
        f"""
        SELECT campaign.id, campaign_budget.id, campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.id = {int(campaign_id)}
        """,
    )
    if not rows:
        return _dump({"alterado": False, "erro": f"campanha {campaign_id} não encontrada"})

    budget_id = _dig(rows[0], "campaignBudget.id")
    anterior = micros_to_units(_dig(rows[0], "campaignBudget.amountMicros"))
    resource = f"customers/{cid}/campaignBudgets/{budget_id}"
    operation = {
        "update": {
            "resourceName": resource,
            "amountMicros": str(int(round(daily_amount * 1_000_000))),
        },
        "updateMask": "amount_micros",
    }
    result = await _client.mutate(
        cid, "campaignBudgets", [operation], validate_only=validate_only
    )
    return _dump(
        {
            "alterado": not validate_only,
            "orcamento_anterior": anterior,
            "orcamento_novo": daily_amount,
            "recurso": resource,
            "resposta": result,
        }
    )


ALL_TOOLS = [
    list_accessible_customers,
    list_client_accounts,
    run_gaql,
    list_campaigns,
    list_ads,
    list_keywords,
    create_responsive_search_ad,
    set_ad_status,
    set_campaign_status,
    set_campaign_budget,
]
