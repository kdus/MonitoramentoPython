-- ********************************************************************************************************
-- * Empresa        : SI Sistemas Inteligentes
-- * Script         : database.sql
-- * Objetivo       : Criação das tabelas para armazenamento dos eventos do VIAWEB Receiver
-- * Data Criação   : 27/01/2026
-- ********************************************************************************************************

CREATE DATABASE IF NOT EXISTS viaweb_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE viaweb_monitoring;

-- Tabela para armazenar os eventos recebidos
CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_recepcao DATETIME NOT NULL,
    data_evento DATETIME NULL,
    id_isep VARCHAR(10) NULL,
    conta_isep VARCHAR(10) NULL,
    codigo_evento VARCHAR(10) NULL,
    particao INT NULL,
    usuario_zona VARCHAR(10) NULL,
    meio_comunicacao VARCHAR(10) NULL,
    equipamento VARCHAR(50) NULL,
    descricao VARCHAR(255) NULL,
    json_completo TEXT NULL,
    processado TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_data_recepcao (data_recepcao),
    INDEX idx_id_isep (id_isep),
    INDEX idx_codigo_evento (codigo_evento),
    INDEX idx_processado (processado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para log de conexões
CREATE TABLE IF NOT EXISTS conexoes_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_conexao DATETIME NOT NULL,
    data_desconexao DATETIME NULL,
    status VARCHAR(50) NULL,
    mensagem TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_data_conexao (data_conexao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para log de erros
CREATE TABLE IF NOT EXISTS erros_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_erro DATETIME NOT NULL,
    tipo_erro VARCHAR(100) NULL,
    mensagem TEXT NULL,
    stack_trace TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_data_erro (data_erro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
