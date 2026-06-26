#!/usr/bin/env python3
# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : test_json_mapping.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Script para testar o mapeamento de JSON para o modelo Evento
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import json
from models.evento import Evento


def test_json_mapping():
    """Testa o mapeamento do JSON de exemplo para o modelo Evento"""
    
    # JSON de exemplo fornecido
    json_exemplo = {
        "id": "12-evento",
        "meio": "ETH",
        "ip": "189.79.61.98",
        "modelo": "VW16ZETH",
        "numSerie": "14951039",
        "isep": "0001",
        "contaCliente": "0001",
        "zonaUsuario": 52,
        "particao": 0,
        "codigoEvento": "1411",
        "minuto": 20,
        "hora": 12,
        "mes": 1,
        "dia": 27,
        "recepcao": 1769527204,
        "portaViaweb": [1733],
        "nomeViaweb": "Servidor VIAWEB",
        "acao": "evento"
    }
    
    print("=" * 80)
    print("TESTE DE MAPEAMENTO JSON -> MODELO EVENTO")
    print("=" * 80)
    print()
    
    print("JSON de entrada:")
    print(json.dumps(json_exemplo, indent=2, ensure_ascii=False))
    print()
    
    # Cria o objeto Evento
    evento = Evento.from_json(json_exemplo)
    
    print("=" * 80)
    print("OBJETO EVENTO CRIADO:")
    print("=" * 80)
    print(f"data_recepcao     : {evento.data_recepcao}")
    print(f"data_evento       : {evento.data_evento}")
    print(f"id_isep           : {evento.id_isep}")
    print(f"conta_isep        : {evento.conta_isep}")
    print(f"codigo_evento     : {evento.codigo_evento}")
    print(f"particao          : {evento.particao}")
    print(f"usuario_zona      : {evento.usuario_zona}")
    print(f"meio_comunicacao  : {evento.meio_comunicacao}")
    print(f"equipamento       : {evento.equipamento}")
    print(f"descricao         : {evento.descricao}")
    print(f"processado        : {evento.processado}")
    print()
    
    print("=" * 80)
    print("VERIFICAÇÃO DOS CAMPOS SOLICITADOS:")
    print("=" * 80)
    print(f"✓ usuario_zona    = {evento.usuario_zona} (esperado: 52)")
    print(f"✓ codigo_evento   = {evento.codigo_evento} (esperado: 1411)")
    print(f"✓ id_isep         = {evento.id_isep} (esperado: 0001)")
    print(f"✓ conta_isep      = {evento.conta_isep} (esperado: 0001)")
    print(f"✓ particao        = {evento.particao} (esperado: 0)")
    print(f"✓ meio_comunicacao= {evento.meio_comunicacao} (esperado: ETH)")
    print(f"✓ equipamento     = {evento.equipamento} (esperado: VW16ZETH 14951039)")
    print(f"✓ data_evento     = {evento.data_evento} (esperado: mes=1 dia=27 hora=12 minuto=20)")
    print(f"✓ data_recepcao   = {evento.data_recepcao}")
    print()
    
    # Validação
    assert evento.usuario_zona == "52", f"Erro: usuario_zona = {evento.usuario_zona}, esperado 52"
    assert evento.codigo_evento == "1411", f"Erro: codigo_evento = {evento.codigo_evento}, esperado 1411"
    assert evento.id_isep == "0001", f"Erro: id_isep = {evento.id_isep}, esperado 0001"
    assert evento.conta_isep == "0001", f"Erro: conta_isep = {evento.conta_isep}, esperado 0001"
    assert evento.particao == 0, f"Erro: particao = {evento.particao}, esperado 0"
    assert evento.meio_comunicacao == "ETH", f"Erro: meio_comunicacao = {evento.meio_comunicacao}, esperado ETH"
    assert evento.equipamento == "VW16ZETH 14951039", f"Erro: equipamento = {evento.equipamento}, esperado VW16ZETH 14951039"

    # data_evento deve refletir os campos dia/mes/hora/minuto do JSON
    assert evento.data_evento is not None, "Erro: data_evento ficou None"
    assert evento.data_evento.month == 1, f"Erro: data_evento.month = {evento.data_evento.month}, esperado 1"
    assert evento.data_evento.day == 27, f"Erro: data_evento.day = {evento.data_evento.day}, esperado 27"
    assert evento.data_evento.hour == 12, f"Erro: data_evento.hour = {evento.data_evento.hour}, esperado 12"
    assert evento.data_evento.minute == 20, f"Erro: data_evento.minute = {evento.data_evento.minute}, esperado 20"

    # data_evento e data_recepcao devem ser distintas (o JSON tem minuto=20,
    # dificilmente coincidente com o minuto atual em que o teste roda).
    assert evento.data_evento != evento.data_recepcao, (
        f"Erro: data_evento ({evento.data_evento}) ficou igual a data_recepcao ({evento.data_recepcao})"
    )

    print("=" * 80)
    print("✓ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 80)


if __name__ == '__main__':
    test_json_mapping()
