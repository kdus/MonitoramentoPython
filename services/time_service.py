# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : time_service.py
# * Linguagem      : Python
# * Objetivo       : Service para fornecer data/hora no fuso local do servidor
# * Data Criação   : 30/06/2026
# ********************************************************************************************************

from __future__ import annotations

import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


def get_timezone_name() -> str:
    """Fuso configurado via .env (APP_TIMEZONE). Padrao: America/Sao_Paulo."""
    return (os.getenv("APP_TIMEZONE", "America/Sao_Paulo") or "America/Sao_Paulo").strip()


def now_local() -> datetime:
    """
    Retorna a data/hora atual no fuso local do servidor como datetime *naive*
    (sem tzinfo), adequado para gravar em colunas DATETIME do MySQL.

    Usa o fuso de APP_TIMEZONE independentemente do relogio do container
    (que por padrao roda em UTC). Em caso de falha, cai para datetime.now().
    """
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo(get_timezone_name())).replace(tzinfo=None)
        except Exception:
            pass
    return datetime.now()
