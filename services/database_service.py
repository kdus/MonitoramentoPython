# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : database_service.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Service para gerenciar conexão e operações com banco de dados
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import os
import mysql.connector
from mysql.connector import Error
from typing import Optional, List
from datetime import datetime
from models.evento import Evento


class DatabaseService:
    """Service responsável por gerenciar operações com banco de dados"""
    
    def __init__(self):
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.database = os.getenv('DB_NAME', 'viaweb_monitoring')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
    
    def connect(self) -> bool:
        """
        Estabelece conexão com o banco de dados
        
        Returns:
            True se conectou com sucesso, False caso contrário
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            if self.connection.is_connected():
                print(f"[DatabaseService] Conectado ao banco de dados {self.database}")
                return True
            return False
        except Error as e:
            print(f"[DatabaseService] Erro ao conectar no banco: {e}")
            return False
    
    def disconnect(self):
        """Fecha conexão com o banco de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[DatabaseService] Desconectado do banco de dados")
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao banco"""
        return self.connection and self.connection.is_connected()
    
    def salvar_evento(self, evento: Evento) -> bool:
        """
        Salva um evento no banco de dados
        
        Args:
            evento: Objeto Evento a ser salvo
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        if not self.is_connected():
            print("[DatabaseService] Nao conectado ao banco de dados", flush=True)
            # Tenta reconectar
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO eventos (
                    data_recepcao, data_evento, id_isep, conta_isep, codigo_evento,
                    particao, usuario_zona, meio_comunicacao, equipamento, descricao,
                    json_completo, processado
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            values = (
                evento.data_recepcao,
                evento.data_evento,
                evento.id_isep,
                evento.conta_isep,
                evento.codigo_evento,
                evento.particao,
                evento.usuario_zona,
                evento.meio_comunicacao,
                evento.equipamento,
                evento.descricao,
                evento.json_completo,
                evento.processado
            )
            cursor.execute(query, values)
            # Commit explícito para garantir que foi salvo
            self.connection.commit()
            evento_id = cursor.lastrowid
            cursor.close()
            # print(f"[DatabaseService] ✓ Evento #{evento_id} salvo com sucesso")
            return True
        except Error as e:
            print(f"[DatabaseService] Erro ao salvar evento: {e}", flush=True)
            # Tenta reconectar em caso de erro
            try:
                self.disconnect()
                self.connect()
            except:
                pass
            return False
    
    def registrar_conexao(self, status: str, mensagem: Optional[str] = None) -> int:
        """
        Registra uma nova conexão no log
        
        Args:
            status: Status da conexão
            mensagem: Mensagem adicional
            
        Returns:
            ID da conexão registrada, ou 0 em caso de erro
        """
        if not self.is_connected():
            return 0
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO conexoes_log (data_conexao, status, mensagem)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (datetime.now(), status, mensagem))
            conexao_id = cursor.lastrowid
            cursor.close()
            return conexao_id
        except Error as e:
            print(f"[DatabaseService] Erro ao registrar conexão: {e}")
            return 0
    
    def atualizar_desconexao(self, conexao_id: int, mensagem: Optional[str] = None):
        """
        Atualiza o registro de desconexão
        
        Args:
            conexao_id: ID da conexão a ser atualizada
            mensagem: Mensagem adicional
        """
        if not self.is_connected() or conexao_id == 0:
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE conexoes_log
                SET data_desconexao = %s, mensagem = CONCAT(COALESCE(mensagem, ''), %s)
                WHERE id = %s
            """
            cursor.execute(query, (datetime.now(), f"\n{mensagem}" if mensagem else "", conexao_id))
            cursor.close()
        except Error as e:
            print(f"[DatabaseService] Erro ao atualizar desconexão: {e}")
    
    def registrar_erro(self, tipo_erro: str, mensagem: str, stack_trace: Optional[str] = None):
        """
        Registra um erro no log
        
        Args:
            tipo_erro: Tipo do erro
            mensagem: Mensagem de erro
            stack_trace: Stack trace do erro
        """
        if not self.is_connected():
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO erros_log (data_erro, tipo_erro, mensagem, stack_trace)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (datetime.now(), tipo_erro, mensagem, stack_trace))
            cursor.close()
        except Error as e:
            print(f"[DatabaseService] Erro ao registrar erro no banco: {e}")
