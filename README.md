# VIAWEB Receiver - Sistema de Monitoramento de Eventos (Python)

Sistema de integração com o VIAWEB Receiver desenvolvido em Python, seguindo o padrão MVC (Model-View-Controller), para receber eventos JSON e gravar em banco de dados MySQL.

## 📋 Descrição

Esta aplicação estabelece uma conexão socket com o VIAWEB Receiver, recebe eventos em tempo real (criptografados com AES-256-CBC), descriptografa, processa e armazena os dados em um banco de dados MySQL para posterior análise.

## 🏗️ Arquitetura

O projeto segue o padrão **MVC + Services**:

```
MonitoramentoPython/
├── models/              # Camada de dados (Model)
│   ├── __init__.py
│   └── evento.py       # Model do Evento
├── controllers/         # Camada de controle (Controller)
│   ├── __init__.py
│   └── monitoring_controller.py
├── services/           # Camada de serviços (Services)
│   ├── __init__.py
│   ├── viaweb_service.py      # Comunicação com VIAWEB Receiver
│   └── database_service.py    # Operações de banco de dados
├── config/
│   └── database.sql    # Script de criação do banco
├── main.py             # Aplicação principal
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de configuração
└── README.md          # Este arquivo
```

## 🔧 Requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior (ou MariaDB 10.2+)
- VIAWEB Receiver configurado e em execução

## 📦 Instalação

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 1.1 Testar mapeamento JSON (Opcional)

Para verificar se o mapeamento dos campos JSON está correto:

```bash
python test_json_mapping.py
```

Este script valida se os campos do JSON estão sendo corretamente mapeados para o banco de dados.

### 2. Criar banco de dados

Execute o script SQL para criar as tabelas:

```bash
mysql -u root -p < config/database.sql
```

Ou importe manualmente pelo MySQL Workbench/phpMyAdmin.

### 3. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
copy .env.example .env
```

Edite o arquivo `.env` e configure os parâmetros:

```env
# Configurações de Conexão VIAWEB Receiver
VIAWEB_HOST=192.168.56.1
VIAWEB_PORT=2700
VIAWEB_AES_KEY=82B861A8B77C50D3ED1EB68D73344E8019DA36E07F0A93F2E160721DE2121C63
VIAWEB_IV_CBC=FCE5B36263C98C6A3C4F50D014E46A06

# Configurações do Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_NAME=viaweb_monitoring
DB_USER=root
DB_PASSWORD=sua_senha_aqui

# Configurações da Aplicação
APP_NAME=Monitoramento Python
APP_LIMITE=1000
PORTA_VIAWEB_MONITORAR=1733
```

**⚠️ IMPORTANTE:** Obtenha os valores corretos de `VIAWEB_AES_KEY` e `VIAWEB_IV_CBC` no Registry do Windows:

```
HKEY_LOCAL_MACHINE\SOFTWARE\SI Sistemas Inteligentes Eletronicos\VIAWEB Receiver\IntegracaoMonitoramento
```

## 🚀 Execução

Execute a aplicação:

```bash
python main.py
```

Para encerrar, pressione `Ctrl+C`.

## 📊 Estrutura do Banco de Dados

### Tabela: `eventos`

Armazena os eventos recebidos do VIAWEB Receiver.

| Campo             | Tipo         | Descrição                          |
|-------------------|--------------|------------------------------------|
| id                | INT          | ID auto-incremento (PK)            |
| data_recepcao     | DATETIME     | Data/hora de recepção              |
| data_evento       | DATETIME     | Data/hora do evento                |
| id_isep           | VARCHAR(10)  | ID do equipamento ISEP             |
| conta_isep        | VARCHAR(10)  | Conta do ISEP                      |
| codigo_evento     | VARCHAR(10)  | Código do evento                   |
| particao          | INT          | Partição                           |
| usuario_zona      | VARCHAR(10)  | Usuário ou zona                    |
| meio_comunicacao  | VARCHAR(10)  | Meio de comunicação (ETH, GPRS...) |
| equipamento       | VARCHAR(50)  | Nome do equipamento                |
| descricao         | VARCHAR(255) | Descrição do evento                |
| json_completo     | TEXT         | JSON completo recebido             |
| processado        | TINYINT(1)   | Flag de processamento              |

### Tabela: `conexoes_log`

Registra conexões e desconexões do sistema.

### Tabela: `erros_log`

Registra erros ocorridos durante a execução.

## 🔐 Segurança

- A comunicação com o VIAWEB Receiver utiliza criptografia **AES-256-CBC**
- As chaves de criptografia devem ser mantidas seguras no arquivo `.env`
- **Nunca** versione o arquivo `.env` com credenciais reais

## 📝 Formato dos Eventos

Exemplo de evento recebido do VIAWEB Receiver:

```json
{
  "oper": [
    {
      "id": "12-evento",
      "acao": "evento",
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
      "nomeViaweb": "Servidor VIAWEB"
    }
  ]
}
```

### Mapeamento JSON → Banco de Dados

| Campo no JSON      | Campo no Banco      | Exemplo          |
|--------------------|---------------------|------------------|
| isep               | id_isep             | "0001"           |
| contaCliente       | conta_isep          | "0001"           |
| codigoEvento       | codigo_evento       | "1411"           |
| zonaUsuario        | usuario_zona        | "52"             |
| particao           | particao            | 0                |
| meio               | meio_comunicacao    | "ETH"            |
| modelo + numSerie  | equipamento         | "VW16ZETH 14951039" |
| recepcao           | data_evento         | timestamp Unix   |

## 🛠️ Customização

### Adicionar novos tipos de processamento

Edite o arquivo `controllers/monitoring_controller.py` no método `_process_operation()`:

```python
def _process_operation(self, operation: Dict[str, Any]):
    acao = operation.get('acao', '')
    
    if acao == 'evento':
        self._process_event(operation)
    elif acao == 'seu_tipo_customizado':
        self._process_custom(operation)
```

### Adicionar campos no banco de dados

1. Adicione o campo na tabela SQL (`config/database.sql`)
2. Atualize o model `models/evento.py`
3. Atualize o método `salvar_evento()` em `services/database_service.py`

## 🐛 Solução de Problemas

### Erro de conexão com VIAWEB Receiver

- Verifique se o VIAWEB Receiver está em execução
- Confirme o IP e porta no arquivo `.env`
- Verifique firewall/antivírus bloqueando a porta 2700

### Erro de chave AES inválida

- Obtenha a chave correta do Registry do Windows
- Certifique-se que está em formato hexadecimal (64 caracteres)

### Erro de conexão com MySQL

- Verifique se o MySQL está rodando
- Confirme usuário e senha no arquivo `.env`
- Execute o script de criação do banco de dados

## 📄 Licença

Desenvolvido por SI Sistemas Inteligentes Eletrônicos.

## 👥 Suporte

Para suporte, entre em contato com SI Sistemas Inteligentes Eletrônicos.
