# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : event_filter_service.py
# * Linguagem      : Python
# * Objetivo       : Service para filtrar eventos antes de gravar no banco de dados
# * Data Criação   : 04/04/2026
# ********************************************************************************************************

from datetime import datetime
from typing import Dict, Optional, Tuple
from models.evento import Evento
from services.logging_service import log


class EventFilterService:
    """
    Service responsável por aplicar regras de filtro nos eventos antes da gravação.

    Regras:
      1. Código de evento: somente gravar eventos cujo codigo_evento comece com '7' ou '8'.
      2. Deduplicação temporal: eventos com todos os campos iguais (exceto data_evento)
         só são gravados se houver pelo menos 25 segundos de diferença do último evento igual.
    """

    PREFIXOS_PERMITIDOS = ('7', '8')
    INTERVALO_MINIMO_SEGUNDOS = 25

    def __init__(self):
        self._ultimo_evento: Dict[str, datetime] = {}

    def _gerar_chave_evento(self, evento: Evento) -> str:
        """Gera uma chave única baseada em todos os campos exceto data_evento e data_recepcao."""
        partes = (
            evento.id_isep or '',
            evento.conta_isep or '',
            evento.codigo_evento or '',
            str(evento.particao) if evento.particao is not None else '',
            evento.usuario_zona or '',
            evento.meio_comunicacao or '',
            evento.equipamento or '',
        )
        return '|'.join(partes)

    def _filtro_codigo_evento(self, evento: Evento) -> Tuple[bool, str]:
        """
        Regra 1: só aceitar codigo_evento que comece com 7 ou 8.
        Retorna (aceito, motivo).
        """
        codigo = evento.codigo_evento or ''
        if not codigo or not codigo.startswith(self.PREFIXOS_PERMITIDOS):
            return False, f"codigo_evento '{codigo}' nao comeca com 7 ou 8"
        return True, ''

    def _filtro_deduplicacao_temporal(self, evento: Evento) -> Tuple[bool, str]:
        """
        Regra 2: rejeitar eventos duplicados cuja data_evento tenha menos de 25s
        de diferença do último evento idêntico gravado.
        Retorna (aceito, motivo).
        """
        if evento.data_evento is None:
            return True, ''

        chave = self._gerar_chave_evento(evento)
        ultima_data = self._ultimo_evento.get(chave)

        if ultima_data is not None:
            diferenca = abs((evento.data_evento - ultima_data).total_seconds())
            if diferenca < self.INTERVALO_MINIMO_SEGUNDOS:
                return False, (
                    f"evento duplicado (diferenca={diferenca:.1f}s < {self.INTERVALO_MINIMO_SEGUNDOS}s)"
                )

        return True, ''

    def registrar_evento_gravado(self, evento: Evento):
        """Atualiza o cache interno após gravação bem-sucedida."""
        if evento.data_evento is not None:
            chave = self._gerar_chave_evento(evento)
            self._ultimo_evento[chave] = evento.data_evento

    def deve_gravar(self, evento: Evento) -> Tuple[bool, str]:
        """
        Aplica todas as regras de filtro sobre o evento.

        Returns:
            (True, '') se o evento deve ser gravado,
            (False, motivo) caso contrário.
        """
        aceito, motivo = self._filtro_codigo_evento(evento)
        if not aceito:
            return False, motivo

        aceito, motivo = self._filtro_deduplicacao_temporal(evento)
        if not aceito:
            return False, motivo

        return True, ''
