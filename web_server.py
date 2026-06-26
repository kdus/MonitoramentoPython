#!/usr/bin/env python3
# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : web_server.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Servidor web para dashboard de monitoramento em tempo real
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.database_service import DatabaseService

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Serviço de banco de dados
db_service = DatabaseService()


@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Retorna o status do sistema"""
    try:
        if not db_service.is_connected():
            db_service.connect()
        
        if not db_service.is_connected():
            return jsonify({
                'status': 'error',
                'message': 'Banco de dados desconectado'
            })
        
        cursor = db_service.connection.cursor(dictionary=True)
        
        # Verifica última conexão
        cursor.execute("""
            SELECT * FROM conexoes_log 
            ORDER BY id DESC LIMIT 1
        """)
        ultima_conexao = cursor.fetchone()
        
        # Conta eventos de hoje
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM eventos 
            WHERE DATE(data_recepcao) = CURDATE()
        """)
        eventos_hoje = cursor.fetchone()['total']
        
        # Conta eventos última hora
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM eventos 
            WHERE data_recepcao >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """)
        eventos_ultima_hora = cursor.fetchone()['total']
        
        # Verifica se está travado (sem eventos há mais de 5 minutos)
        cursor.execute("""
            SELECT MAX(data_recepcao) as ultima_recepcao 
            FROM eventos
        """)
        result = cursor.fetchone()
        ultima_recepcao = result['ultima_recepcao'] if result else None
        
        travado = False
        tempo_sem_evento = None
        if ultima_recepcao:
            tempo_sem_evento = (datetime.now() - ultima_recepcao).total_seconds()
            travado = tempo_sem_evento > 300  # 5 minutos
        
        # Status da conexão
        sistema_online = False
        if ultima_conexao and not ultima_conexao['data_desconexao']:
            sistema_online = True
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'sistema_online': sistema_online,
            'travado': travado,
            'tempo_sem_evento': tempo_sem_evento,
            'eventos_hoje': eventos_hoje,
            'eventos_ultima_hora': eventos_ultima_hora,
            'ultima_conexao': ultima_conexao['data_conexao'].isoformat() if ultima_conexao else None,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/api/eventos')
def get_eventos():
    """Retorna os últimos eventos"""
    from flask import request
    
    try:
        limit = int(request.args.get('limit', 50))
        
        if not db_service.is_connected():
            db_service.connect()
        
        cursor = db_service.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, data_recepcao, data_evento, id_isep, conta_isep, 
                   codigo_evento, usuario_zona, meio_comunicacao, 
                   equipamento, descricao
            FROM eventos 
            ORDER BY id DESC 
            LIMIT %s
        """, (limit,))
        
        eventos = cursor.fetchall()
        cursor.close()
        
        # Converte datetime para string
        for evento in eventos:
            if evento['data_recepcao']:
                evento['data_recepcao'] = evento['data_recepcao'].isoformat()
            if evento['data_evento']:
                evento['data_evento'] = evento['data_evento'].isoformat()
        
        return jsonify({
            'status': 'success',
            'eventos': eventos
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/api/estatisticas')
def get_estatisticas():
    """Retorna estatísticas dos eventos"""
    try:
        if not db_service.is_connected():
            db_service.connect()
        
        cursor = db_service.connection.cursor(dictionary=True)
        
        # Total de eventos
        cursor.execute("SELECT COUNT(*) as total FROM eventos")
        total_eventos = cursor.fetchone()['total']
        
        # Eventos por código
        cursor.execute("""
            SELECT codigo_evento, COUNT(*) as total 
            FROM eventos 
            WHERE codigo_evento IS NOT NULL
            GROUP BY codigo_evento 
            ORDER BY total DESC 
            LIMIT 10
        """)
        eventos_por_codigo = cursor.fetchall()
        
        # Eventos por ISEP
        cursor.execute("""
            SELECT id_isep, equipamento, COUNT(*) as total 
            FROM eventos 
            WHERE id_isep IS NOT NULL
            GROUP BY id_isep, equipamento 
            ORDER BY total DESC 
            LIMIT 10
        """)
        eventos_por_isep = cursor.fetchall()
        
        # Eventos por hora (últimas 24h)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(data_recepcao, '%Y-%m-%d %H:00:00') as hora,
                COUNT(*) as total 
            FROM eventos 
            WHERE data_recepcao >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY hora 
            ORDER BY hora
        """)
        eventos_por_hora = cursor.fetchall()
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'total_eventos': total_eventos,
            'eventos_por_codigo': eventos_por_codigo,
            'eventos_por_isep': eventos_por_isep,
            'eventos_por_hora': eventos_por_hora
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


if __name__ == '__main__':
    # Conecta ao banco de dados
    db_service.connect()
    
    print("=" * 80)
    print("   DASHBOARD WEB - VIAWEB Receiver Monitoring")
    print("   Servidor iniciando...")
    print("=" * 80)
    print()
    print("   Acesse: http://localhost:5000")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
