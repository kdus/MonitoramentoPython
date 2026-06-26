# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : monitoring_controller.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Controller para coordenar o monitoramento de eventos
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import os
import time
import traceback
from datetime import datetime
from typing import Dict, Any
from services.viaweb_service import ViawebService
from services.database_service import DatabaseService
from services.event_filter_service import EventFilterService
from services.logging_service import log, log_evento
from models.evento import Evento


class MonitoringController:
    """Controller responsável por coordenar o monitoramento de eventos"""
    
    def __init__(self):
        self.viaweb_service = ViawebService()
        self.db_service = DatabaseService()
        self.event_filter = EventFilterService()
        self.running = False
        self.conexao_id = 0
        self._disconnect_streak = 0
        self._last_heartbeat_ts = 0.0
    
    def _ts(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log(self, msg: str):
        # Em producao, LOG_LEVEL=ERROR deixa isso silencioso.
        log("INFO", msg)
    
    def start(self):
        """Inicia o monitoramento de eventos (loop infinito com auto-recovery)"""
        self._log("[MonitoringController] Iniciando monitoramento...")

        self.running = True

        while self.running:
            try:
                self._run_cycle()
            except KeyboardInterrupt:
                self._log("[MonitoringController] Interrompido pelo usuario")
                break
            except Exception as e:
                self._log(f"[MonitoringController] Erro inesperado: {e}")
                traceback.print_exc()
                try:
                    self.db_service.registrar_erro(
                        tipo_erro=type(e).__name__,
                        mensagem=str(e),
                        stack_trace=traceback.format_exc()
                    )
                except Exception:
                    pass

            if not self.running:
                break

            self._log("[MonitoringController] Reiniciando ciclo em 10s...")
            time.sleep(10)

        self._cleanup("Monitoramento encerrado")

    def _run_cycle(self):
        """Executa um ciclo completo de monitoramento (reconecta BD e VIAWEB)"""
        if not self.db_service.connect():
            self._log("[MonitoringController] ERRO: Nao foi possivel conectar ao banco de dados. Retry em breve.")
            return

        tentativas_reconexao = 0

        while self.running:
            # Heartbeat a cada 60s (para confirmar que esta vivo mesmo sem eventos)
            now = time.time()
            heartbeat_sec = int(os.getenv("HEARTBEAT_SEC", "0") or 0)
            if heartbeat_sec > 0 and (now - self._last_heartbeat_ts >= heartbeat_sec):
                self._last_heartbeat_ts = now
                self._log("[MonitoringController] Heartbeat: monitoramento ativo.")

            if not self.viaweb_service.connected:
                tentativas_reconexao += 1
                self._log(f"[MonitoringController] Tentativa de conexao {tentativas_reconexao}...")

                if not self.viaweb_service.connect():
                    wait = min(5 * tentativas_reconexao, 60)
                    self._log(f"[MonitoringController] Falha. Aguardando {wait}s antes de tentar reconectar...")
                    time.sleep(wait)
                    continue

                tentativas_reconexao = 0
                # Conectou: zera streak de desconexoes
                self._disconnect_streak = 0
                self.conexao_id = self.db_service.registrar_conexao("Conectado", "Conexao estabelecida com sucesso")

                if not self.viaweb_service.send_identification():
                    self._log("[MonitoringController] ERRO: Nao foi possivel enviar identificacao")
                    self.viaweb_service.disconnect()
                    time.sleep(5)
                    continue

                self._log("[MonitoringController] ========================================")
                self._log("[MonitoringController] MONITORAMENTO ATIVO - AGUARDANDO EVENTOS")
                self._log("[MonitoringController] ========================================")

            if not self.viaweb_service.receive_messages(self._process_operation):
                self._disconnect_streak += 1
                wait = min(2 ** min(self._disconnect_streak, 6), 60)  # 2,4,8,16,32,60...
                log("WARN", f"[MonitoringController] Conexao perdida. Tentando reconectar (backoff {wait}s)...")
                if self.conexao_id > 0:
                    self.db_service.atualizar_desconexao(self.conexao_id, "Conexao perdida - reconectando")
                    self.conexao_id = 0
                time.sleep(wait)
                continue

            time.sleep(0.05)
    
    def stop(self):
        """Para o monitoramento de eventos"""
        self._log("[MonitoringController] Parando monitoramento...")
        self.running = False
    
    def _process_operation(self, operation: Dict[str, Any]):
        """
        Processa uma operação recebida do VIAWEB Receiver
        
        Args:
            operation: Dicionário com dados da operação
        """
        try:
            acao = operation.get('acao', '')
            
            if acao == 'evento':
                # Evento recebido - processar e salvar no banco
                # Log conciso (INFO): em producao pode ficar silencioso (LOG_LEVEL=ERROR).
                self._log("[MonitoringController] EVENTO recebido")
                self._process_event(operation)
                self._log("[MonitoringController] Evento processado. Continuando escuta.")
            
            elif acao == 'ping':
                # Ping e ruido: so aparece se LOG_LEVEL=DEBUG (via ViawebService) ou INFO (se habilitado).
                self._log("[MonitoringController] Ping recebido - conexao ativa")
            
            else:
                self._log(f"[MonitoringController] Operacao recebida: {acao}")
        
        except Exception as e:
            self._log(f"[MonitoringController] ERRO ao processar operacao: {e}")
            traceback.print_exc()
            self.db_service.registrar_erro(
                tipo_erro=type(e).__name__,
                mensagem=f"Erro ao processar operação: {str(e)}",
                stack_trace=traceback.format_exc()
            )
    
    def _process_event(self, event_data: Dict[str, Any]):
        """
        Processa um evento recebido e salva no banco de dados
        
        Args:
            event_data: Dicionário com dados do evento
        """
        try:
            evento = Evento.from_json(event_data)
            
            self._log(
                "[MonitoringController] Evento "
                f"(recebido={evento.data_recepcao} evento={evento.data_evento}) "
                f"ISEP={evento.id_isep} Conta={evento.conta_isep} Codigo={evento.codigo_evento} "
                f"Zona/Usuario={evento.usuario_zona} Meio={evento.meio_comunicacao} Equip={evento.equipamento}"
            )
            
            aceito, motivo = self.event_filter.deve_gravar(evento)
            if not aceito:
                self._log(f"[MonitoringController] Evento FILTRADO - {motivo}")
                return
            
            if self.db_service.salvar_evento(evento):
                self.event_filter.registrar_evento_gravado(evento)
                log_evento(evento)
                self._log(f"[MonitoringController] OK Evento {evento.id_isep}-{evento.codigo_evento} salvo.")
            else:
                log("ERROR", f"[MonitoringController] FALHA ao salvar evento: {evento}")
                self.db_service.registrar_erro(
                    tipo_erro="DatabaseError",
                    mensagem=f"Falha ao salvar evento: {evento}",
                    stack_trace=None
                )
        
        except Exception as e:
            self._log(f"[MonitoringController] ERRO ao processar evento: {e}")
            traceback.print_exc()
            self.db_service.registrar_erro(
                tipo_erro=type(e).__name__,
                mensagem=f"Erro ao processar evento: {str(e)}",
                stack_trace=traceback.format_exc()
            )
    
    def _cleanup(self, mensagem: str):
        """
        Limpa recursos e desconecta serviços
        
        Args:
            mensagem: Mensagem a ser registrada no log
        """
        # Atualiza log de desconexão
        if self.conexao_id > 0:
            self.db_service.atualizar_desconexao(self.conexao_id, mensagem)
        
        # Desconecta serviços
        self.viaweb_service.disconnect()
        self.db_service.disconnect()
        
        self._log(f"[MonitoringController] {mensagem}")
