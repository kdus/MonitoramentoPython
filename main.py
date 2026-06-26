#!/usr/bin/env python3
# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : main.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Aplicação principal para monitoramento do VIAWEB Receiver
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import os
import signal
import sys
import time
from dotenv import load_dotenv
from controllers.monitoring_controller import MonitoringController


def _configure_stdio_windows() -> None:
    """Evita UnicodeEncodeError em logs redirecionados (cp1252) no Windows."""
    if sys.platform != "win32":
        return
    try:
        stdout = getattr(sys.stdout, "reconfigure", None)
        stderr = getattr(sys.stderr, "reconfigure", None)
        if callable(stdout):
            stdout(encoding="utf-8", errors="replace")
        if callable(stderr):
            stderr(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    _configure_stdio_windows()
    print("=" * 80, flush=True)
    print("   VIAWEB Receiver - Sistema de Monitoramento de Eventos (Python)", flush=True)
    print("   SI Sistemas Inteligentes Eletronicos", flush=True)
    print("   Versao 1.0 - Escuta continua 24/7 (auto-recovery)", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    while True:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            print("[Main] OK: Arquivo .env carregado com sucesso", flush=True)
        else:
            print(f"[Main] AVISO: Arquivo .env nao encontrado em {env_path}", flush=True)
            print("[Main] Copie o arquivo .env.example para .env e configure-o", flush=True)

        print(flush=True)

        if not os.getenv('VIAWEB_AES_KEY'):
            print("[Main] ERRO: VIAWEB_AES_KEY nao configurada no .env. Tentando novamente em 60s...", flush=True)
            time.sleep(60)
            continue

        if not os.getenv('VIAWEB_IV_CBC'):
            print("[Main] ERRO: VIAWEB_IV_CBC nao configurada no .env. Tentando novamente em 60s...", flush=True)
            time.sleep(60)
            continue

        break

    print(f"[Main] VIAWEB Receiver: {os.getenv('VIAWEB_HOST')}:{os.getenv('VIAWEB_PORT')}", flush=True)
    print(f"[Main] Banco de Dados: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}", flush=True)
    print(f"[Main] Aplicacao: {os.getenv('APP_NAME')}", flush=True)
    print(flush=True)
    print("[Main] Modo: servico continuo (auto-recovery). Ctrl+C para encerrar.", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)

    controller = MonitoringController()

    def _shutdown(signum, frame):
        print(f"\n[Main] Sinal {signum} recebido. Encerrando...", flush=True)
        controller.stop()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _shutdown)

    try:
        controller.start()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()

    print(flush=True)
    print("=" * 80, flush=True)
    print("   Aplicacao encerrada", flush=True)
    print("=" * 80, flush=True)


if __name__ == '__main__':
    main()
