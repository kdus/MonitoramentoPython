from __future__ import annotations

import os
from datetime import datetime
from typing import Final, Literal

LogLevel = Literal["ERROR", "WARN", "INFO", "DEBUG"]

_LEVELS: Final[dict[str, int]] = {"ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10}

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EVENTO_LOG = os.path.join(_SCRIPT_DIR, "logs", "Evento.log")


def _env_level() -> str:
    raw = (os.getenv("LOG_LEVEL", "ERROR") or "ERROR").strip().upper()
    return raw if raw in _LEVELS else "ERROR"


def enabled(level: LogLevel) -> bool:
    return _LEVELS[level] >= _LEVELS[_env_level()]


def log(level: LogLevel, msg: str) -> None:
    if not enabled(level):
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def log_auto(msg: str) -> None:
    up = msg.upper()
    if any(k in up for k in ("ERRO", "FALHA", "EXCEPTION", "TRACEBACK")):
        log("ERROR", msg)
        return
    if any(k in up for k in ("AVISO", "WARN")):
        log("WARN", msg)
        return
    log("INFO", msg)


def log_evento(evento) -> None:
    """Grava uma linha de log no arquivo logs/Evento.log sempre que um evento é salvo no banco."""
    try:
        os.makedirs(os.path.dirname(_EVENTO_LOG), exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = (
            f"[{ts}] "
            f"data_evento={evento.data_evento} "
            f"ISEP={evento.id_isep} "
            f"Conta={evento.conta_isep} "
            f"Codigo={evento.codigo_evento} "
            f"Particao={evento.particao} "
            f"Zona/Usuario={evento.usuario_zona} "
            f"Meio={evento.meio_comunicacao} "
            f"Equip={evento.equipamento} "
            f"Descricao={evento.descricao}"
        )
        with open(_EVENTO_LOG, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception as e:
        log("ERROR", f"[LogService] Erro ao gravar Evento.log: {e}")

