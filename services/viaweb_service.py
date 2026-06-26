# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Script         : viaweb_service.py
# * Programador    : Sistema de IA
# * Linguagem      : Python
# * Objetivo       : Service para comunicação com VIAWEB Receiver
# * Data Criação   : 27/01/2026
# ********************************************************************************************************

import socket
import json
import os
import time
from typing import Optional, Callable, Dict, Any
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from services.logging_service import log, log_auto


class ViawebService:
    """Service responsável por gerenciar comunicação com VIAWEB Receiver"""
    
    def __init__(self):
        self.host = os.getenv('VIAWEB_HOST', '192.168.56.1')
        self.port = int(os.getenv('VIAWEB_PORT', '2700'))
        self.aes_key = bytes.fromhex(os.getenv('VIAWEB_AES_KEY', ''))
        self.iv_cbc = bytes.fromhex(os.getenv('VIAWEB_IV_CBC', ''))
        self.iv_send = bytearray(self.iv_cbc)
        self.iv_recv = bytearray(self.iv_cbc)
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.buffer_recv = bytearray()
        self.buffer_decrypted = bytearray()
        self.operation_id = 1
        
        self.app_name = os.getenv('APP_NAME', 'Monitoramento Python')
        self.app_limite = int(os.getenv('APP_LIMITE', '1000'))
        self.porta_viaweb = int(os.getenv('PORTA_VIAWEB_MONITORAR', '1733'))
    
    def connect(self) -> bool:
        """
        Estabelece conexão socket com VIAWEB Receiver
        
        Returns:
            True se conectou com sucesso, False caso contrário
        """
        try:
            log("INFO", f"[ViawebService] Conectando em {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # 10 segundos de timeout na conexão
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(0.01)  # 10ms de timeout na recepção
            
            # Reseta os IVs
            self.iv_send = bytearray(self.iv_cbc)
            self.iv_recv = bytearray(self.iv_cbc)
            self.connected = True
            
            log("INFO", "[ViawebService] Conectado com sucesso!")
            return True
            
        except socket.timeout:
            log("WARN", "[ViawebService] Timeout ao conectar")
            return False
        except socket.error as e:
            log("WARN", f"[ViawebService] Erro ao conectar: {e}")
            return False
        except Exception as e:
            log("ERROR", f"[ViawebService] Erro inesperado ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do VIAWEB Receiver"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        log("INFO", "[ViawebService] Desconectado")
    
    def send_identification(self) -> bool:
        """
        Envia identificação e inicia monitoramento de eventos
        
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        msg = {
            "ts": int(time.time() * 1000),
            "oper": [
                {
                    "id": self.operation_id,
                    "acao": "ident",
                    "nome": self.app_name,
                    "limite": self.app_limite,
                    "versaoProto": 1
                },
                {
                    "id": self.operation_id + 1,
                    "acao": "salvarVIAWEB",
                    "operacao": 2,
                    "porta": self.porta_viaweb,
                    "monitoramento": 1,
                    "descarteEventos": -1
                }
            ]
        }
        self.operation_id += 2
        
        json_str = json.dumps(msg, ensure_ascii=False)
        # Muito verboso em producao: fica para DEBUG
        log("DEBUG", f"[ViawebService] Enviando identificacao: {json_str}")
        return self._send_json(json_str)
    
    def _send_json(self, json_str: str) -> bool:
        """
        Envia uma mensagem JSON criptografada
        
        Args:
            json_str: String JSON a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        if not self.connected or not self.socket:
            log("WARN", "[ViawebService] Socket nao conectado")
            return False
        
        try:
            # Criptografa com AES-256-CBC
            cipher = AES.new(self.aes_key, AES.MODE_CBC, bytes(self.iv_send))
            encrypted = cipher.encrypt(pad(json_str.encode('utf-8'), AES.block_size))
            
            # Salva o novo IV (últimos 16 bytes do criptografado)
            self.iv_send = bytearray(encrypted[-16:])
            
            # Envia os dados
            self.socket.sendall(encrypted)
            return True
            
        except Exception as e:
            log("WARN", f"[ViawebService] Erro ao enviar JSON: {e}")
            self.disconnect()
            return False
    
    def send_response(self, operation_ids: list) -> bool:
        """
        Envia resposta para operações recebidas
        
        Args:
            operation_ids: Lista de IDs das operações a responder
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        if not operation_ids:
            return True
        
        msg = {
            "resp": [{"id": op_id} for op_id in operation_ids]
        }
        
        json_str = json.dumps(msg, ensure_ascii=False)
        log("DEBUG", f"[ViawebService] Enviando resposta: {json_str}")
        return self._send_json(json_str)
    
    def receive_messages(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Recebe e processa mensagens do VIAWEB Receiver
        
        Args:
            callback: Função a ser chamada para cada operação recebida
            
        Returns:
            True se continua conectado, False se desconectou
        """
        if not self.connected or not self.socket:
            return False
        
        try:
            # Tenta receber dados (com timeout de 10ms)
            try:
                data = self.socket.recv(65536)
                if len(data) == 0:
                    # Conexão fechada pelo servidor
                    log("WARN", "[ViawebService] Conexao fechada pelo servidor")
                    self.disconnect()
                    return False
                
                # Adiciona ao buffer de recepção
                self.buffer_recv.extend(data)
                # print(f"[ViawebService] {len(data)} bytes recebidos")
                
            except socket.timeout:
                # Timeout normal, sem dados para receber - continua escutando
                return True
            except socket.error as e:
                # Erro no socket
                log("WARN", f"[ViawebService] Erro no socket: {e}")
                self.disconnect()
                return False
            
            # Descriptografa em blocos de 16 bytes
            while len(self.buffer_recv) >= 16:
                # Pega blocos múltiplos de 16
                block_size = (len(self.buffer_recv) // 16) * 16
                encrypted_data = bytes(self.buffer_recv[:block_size])
                self.buffer_recv = self.buffer_recv[block_size:]
                
                # Descriptografa
                cipher = AES.new(self.aes_key, AES.MODE_CBC, bytes(self.iv_recv))
                decrypted = cipher.decrypt(encrypted_data)
                
                # Salva o novo IV (últimos 16 bytes do criptografado)
                self.iv_recv = bytearray(encrypted_data[-16:])
                
                # Remove padding e adiciona ao buffer descriptografado
                try:
                    unpadded = unpad(decrypted, AES.block_size)
                    self.buffer_decrypted.extend(unpadded)
                except ValueError:
                    # Padding inválido, pode ser mensagem incompleta
                    self.buffer_decrypted.extend(decrypted.rstrip(b'\x00'))
            
            # Processa JSONs completos no buffer descriptografado
            self._process_json_buffer(callback)
            
            # Sempre retorna True para continuar escutando
            return True
            
        except Exception as e:
            log("ERROR", f"[ViawebService] Erro ao receber mensagens: {e}")
            import traceback
            traceback.print_exc()
            self.disconnect()
            return False
    
    def _process_json_buffer(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Processa o buffer descriptografado buscando JSONs completos
        
        Args:
            callback: Função a ser chamada para cada operação recebida
        """
        try:
            json_str = self.buffer_decrypted.decode('utf-8')
        except UnicodeDecodeError:
            return
        
        # Separa mensagens JSON contando chaves
        inicio_json = 0
        conta_chaves = 0
        i = 0
        
        while i < len(json_str):
            if json_str[i] == '{':
                conta_chaves += 1
            elif json_str[i] == '}':
                conta_chaves -= 1
                if conta_chaves == 0:
                    # JSON completo encontrado
                    json_completo = json_str[inicio_json:i+1]
                    try:
                        obj = json.loads(json_completo)
                        # Mensagem completa e muito verbosa: DEBUG
                        log("DEBUG", f"[ViawebService] Mensagem recebida: {json_completo[:500]}{'...' if len(json_completo) > 500 else ''}")
                        self._process_message(obj, callback)
                    except json.JSONDecodeError as e:
                        log("WARN", f"[ViawebService] Erro ao decodificar JSON: {e}")
                    
                    inicio_json = i + 1
            i += 1
        
        # Remove a parte processada do buffer
        if inicio_json > 0:
            self.buffer_decrypted = bytearray(json_str[inicio_json:].encode('utf-8'))
    
    def _process_message(self, obj: Dict[str, Any], callback: Callable[[Dict[str, Any]], None]):
        """
        Processa uma mensagem JSON recebida
        
        Args:
            obj: Objeto JSON recebido
            callback: Função a ser chamada para cada operação recebida
        """
        # Processa respostas (resp)
        if 'resp' in obj:
            for resp in obj['resp']:
                if 'erro' in resp:
                    log("WARN", f"[ViawebService] ERRO na resposta: {resp.get('descricao', 'Erro desconhecido')}")
        
        # Processa operações (oper)
        if 'oper' in obj:
            operation_ids = []
            for oper in obj['oper']:
                op_id = oper.get('id')
                operation_ids.append(op_id)
                
                # Chama o callback para processar a operação
                try:
                    callback(oper)
                except Exception as e:
                    log("ERROR", f"[ViawebService] Erro no callback: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Responde todas as operações recebidas
            if operation_ids:
                self.send_response(operation_ids)
