# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : evento.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Model para representar um evento do VIAWEB Receiver
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

from datetime import datetime
from typing import Optional, Dict, Any


class Evento:
    """Model que representa um evento recebido do VIAWEB Receiver"""
    
    def __init__(
        self,
        data_recepcao: datetime,
        data_evento: Optional[datetime] = None,
        id_isep: Optional[str] = None,
        conta_isep: Optional[str] = None,
        codigo_evento: Optional[str] = None,
        particao: Optional[int] = None,
        usuario_zona: Optional[str] = None,
        meio_comunicacao: Optional[str] = None,
        equipamento: Optional[str] = None,
        descricao: Optional[str] = None,
        json_completo: Optional[str] = None,
        processado: bool = False
    ):
        self.data_recepcao = data_recepcao
        self.data_evento = data_evento
        self.id_isep = id_isep
        self.conta_isep = conta_isep
        self.codigo_evento = codigo_evento
        self.particao = particao
        self.usuario_zona = usuario_zona
        self.meio_comunicacao = meio_comunicacao
        self.equipamento = equipamento
        self.descricao = descricao
        self.json_completo = json_completo
        self.processado = processado
    
    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Evento':
        """
        Cria um objeto Evento a partir de dados JSON do VIAWEB Receiver
        
        Args:
            json_data: Dicionário com os dados do evento
            
        Returns:
            Instância de Evento
        """
        import json
        
        # Monta data_evento a partir dos campos dia/mes/hora/minuto do JSON
        # (data/hora real ocorrida no equipamento). Como o JSON não traz ano nem
        # segundo, derivamos esses componentes do timestamp Unix 'recepcao'
        # quando disponível; caso contrário, usamos o ano atual e segundo = 0.
        data_evento = None
        recepcao_timestamp = json_data.get('recepcao')

        dia = json_data.get('dia')
        mes = json_data.get('mes')
        hora = json_data.get('hora')
        minuto = json_data.get('minuto')

        if all(v is not None for v in [dia, mes, hora, minuto]):
            try:
                if recepcao_timestamp:
                    base = datetime.fromtimestamp(recepcao_timestamp)
                    ano = base.year
                    segundo = base.second
                else:
                    ano = datetime.now().year
                    segundo = 0
                data_evento = datetime(ano, mes, dia, hora, minuto, segundo)
            except (ValueError, TypeError, OSError):
                data_evento = None

        # Fallback final: se não conseguiu montar pelos campos dia/mes/hora/minuto,
        # usa o timestamp Unix de recepção.
        if data_evento is None and recepcao_timestamp:
            try:
                data_evento = datetime.fromtimestamp(recepcao_timestamp)
            except (ValueError, TypeError, OSError):
                pass
        
        # Monta a descrição do equipamento
        equipamento = None
        modelo = json_data.get('modelo')
        num_serie = json_data.get('numSerie')
        if modelo and num_serie:
            equipamento = f"{modelo} {num_serie}"
        elif modelo:
            equipamento = modelo
        
        # Monta uma descrição do evento
        descricao = None
        codigo_evento = json_data.get('codigoEvento')
        zona_usuario = json_data.get('zonaUsuario')
        if codigo_evento:
            if zona_usuario:
                descricao = f"COD. {codigo_evento} Zona {zona_usuario}"
            else:
                descricao = f"COD. {codigo_evento}"
        
        # Converte zonaUsuario para string se necessário
        usuario_zona_val = json_data.get('zonaUsuario')
        if usuario_zona_val is not None:
            usuario_zona_str = str(usuario_zona_val)
        else:
            usuario_zona_str = None
        
        return Evento(
            data_recepcao=datetime.now(),
            data_evento=data_evento,
            id_isep=json_data.get('isep'),  # Mapeamento correto: isep
            conta_isep=json_data.get('contaCliente'),  # Mapeamento correto: contaCliente
            codigo_evento=json_data.get('codigoEvento'),  # Mapeamento correto: codigoEvento
            particao=json_data.get('particao'),
            usuario_zona=usuario_zona_str,  # Mapeamento correto: zonaUsuario
            meio_comunicacao=json_data.get('meio'),  # Mapeamento correto: meio
            equipamento=equipamento,  # Montado a partir de modelo + numSerie
            descricao=descricao,  # Montado automaticamente
            json_completo=json.dumps(json_data, ensure_ascii=False),
            processado=False
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto Evento para dicionário
        
        Returns:
            Dicionário com os dados do evento
        """
        return {
            'data_recepcao': self.data_recepcao,
            'data_evento': self.data_evento,
            'id_isep': self.id_isep,
            'conta_isep': self.conta_isep,
            'codigo_evento': self.codigo_evento,
            'particao': self.particao,
            'usuario_zona': self.usuario_zona,
            'meio_comunicacao': self.meio_comunicacao,
            'equipamento': self.equipamento,
            'descricao': self.descricao,
            'json_completo': self.json_completo,
            'processado': self.processado
        }
    
    def __repr__(self) -> str:
        return (f"Evento(id_isep={self.id_isep}, codigo={self.codigo_evento}, "
                f"data_evento={self.data_evento})")
