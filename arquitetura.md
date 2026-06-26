# Arquitetura — MonitoramentoPython (VIAWEB Receiver)

Aplicação em **Python** para manter uma conexão com o **VIAWEB Receiver**, receber mensagens criptografadas (**AES-256-CBC**), processar eventos e persistir em **MySQL**, seguindo o padrão **MVC + Services**. O objetivo operacional é rodar **24/7** com recuperação automática (reconexão, watchdog e reinício).

---

## 1) Visão geral (MVC + Services)

| Camada | Responsabilidade | Arquivos principais |
|-------|-------------------|-------------------|
| **Model** | Estrutura e mapeamento do evento | `models/evento.py` |
| **Controller** | Orquestra o ciclo de vida, reconexões, processamento do evento | `controllers/monitoring_controller.py` |
| **Services** | Integrações e regras técnicas (socket/cripto, banco) | `services/viaweb_service.py`, `services/database_service.py` |
| **Entry (Main)** | Bootstrap, `.env`, sinais e configuração de I/O | `main.py` |
| **Infra (Windows)** | Execução resiliente via watchdog + tarefa agendada | `iniciar.bat`, `instalar_servico.bat`, `desinstalar_servico.bat`, `MonitoramentoPython_task.xml` |

> **View**: não há UI. A “saída” do sistema é o **log** (stdout/stderr redirecionado para arquivo pelo watchdog) e o **banco**.

---

## 2) Estrutura de diretórios (resumo)

```
MonitoramentoPython/
├── main.py
├── controllers/
│   └── monitoring_controller.py
├── models/
│   └── evento.py
├── services/
│   ├── viaweb_service.py
│   └── database_service.py
├── config/
│   └── database.sql
├── iniciar.bat
├── instalar_servico.bat
├── desinstalar_servico.bat
├── MonitoramentoPython_task.xml
├── logs/
│   └── Ptytho-MonitoramentoViaweb.log
├── requirements.txt
├── .env.example
└── README.md
```

---

## 3) Fluxo ponta a ponta (dados)

1. **Bootstrap**
   - `main.py` carrega `.env` (ou re-tenta se chave/IV não estiverem configurados).
   - No Windows, configura stdout/stderr em **UTF-8** (`errors="replace"`) para evitar `UnicodeEncodeError` com saída redirecionada.
2. **Controller inicia**
   - `MonitoringController.start()` entra em loop “infinito” e chama `_run_cycle()`.
3. **Banco**
   - `DatabaseService.connect()` abre conexão MySQL com `autocommit=True` (e commit explícito no insert do evento).
4. **Socket / Protocolo**
   - `ViawebService.connect()` abre TCP para `VIAWEB_HOST:VIAWEB_PORT`.
   - `ViawebService.send_identification()` envia `ident` e `salvarVIAWEB` criptografados (AES-CBC), com IV encadeado.
5. **Recepção**
   - `ViawebService.receive_messages()` faz `recv` com timeout curto, alimenta buffers e tenta descriptografar em blocos.
   - Ao formar JSON completo, chama callback do controller por operação.
6. **Processamento**
   - Para `acao=evento`, `Evento.from_json()` cria o model e `DatabaseService.salvar_evento()` persiste.
7. **Respostas**
   - `ViawebService.send_response()` responde IDs recebidos (ACK).

---

## 4) Resiliência (não parar nunca)

A resiliência aqui é composta por **3 níveis**:

### 4.1) Loop interno (aplicação)

No `MonitoringController`:

- **Reconexão automática** quando o socket cai (ex.: `WinError 10054`).
- **Backoff progressivo** em quedas seguidas para evitar loop agressivo:
  - espera \(2, 4, 8, 16, 32, até 60s\) antes de nova tentativa.
- **Heartbeat**: a cada ~60s imprime um log “monitoramento ativo”, útil quando não há eventos.
- Se uma exceção escapar do ciclo, o controller espera 10s e reinicia o ciclo.

### 4.2) Watchdog de processo (Windows)

`iniciar.bat` executa `python -u main.py` e, se o processo encerrar por qualquer motivo, ele **reinicia** após alguns segundos, anexando saída em arquivo:

- Log padrão: `logs/Ptytho-MonitoramentoViaweb.log`
- Também força `chcp 65001` para garantir UTF‑8 no console.

### 4.3) Supervisão do Windows (Tarefa Agendada)

`instalar_servico.bat` instala uma **Tarefa Agendada** (SYSTEM no boot), que chama o `iniciar.bat`.

O template `MonitoramentoPython_task.xml` usa:

- **Boot trigger** (subir no boot)
- **Repetição a cada 1 minuto** (se parar, tende a voltar rápido)
- `MultipleInstancesPolicy=IgnoreNew` (não cria múltiplas instâncias simultâneas)

---

## 5) Observabilidade e logs

### 5.1) Formato recomendado

O controller prefixa logs com timestamp:

- `[YYYY-MM-DD HH:MM:SS] [MonitoringController] ...`

Para evento, também registra:

- Data/hora do evento (quando disponível)
- Data/hora de recepção (sempre)
- Campos principais (ISEP, conta, código, zona/usuário, etc.)

### 5.2) Onde olhar

- **Arquivo de log**: `logs/Ptytho-MonitoramentoViaweb.log`
- **Banco**:
  - `eventos` (eventos recebidos)
  - `conexoes_log` (conectou/desconectou)
  - `erros_log` (erros registrados)

---

## 6) Configuração (sem expor segredos)

As variáveis ficam no `.env` (não versionar em produção). O `.env.example` serve como base.

Principais grupos:

### 6.1) VIAWEB

- `VIAWEB_HOST`, `VIAWEB_PORT`
- `VIAWEB_AES_KEY` (hex)
- `VIAWEB_IV_CBC` (hex)
- `PORTA_VIAWEB_MONITORAR`

### 6.2) MySQL

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### 6.3) Aplicação

- `APP_NAME`, `APP_LIMITE`

> **Segurança**: nunca commitar `.env` real. Chaves AES e senha do banco são credenciais.

---

## 7) Principais pontos de falha e mitigação

| Risco | Sintoma | Mitigação implementada |
|------|---------|------------------------|
| Queda de rede / servidor fecha conexão | `WinError 10054`, desconexões em sequência | reconexão + backoff progressivo |
| Loop agressivo de reconexão | CPU/log alto, instabilidade | backoff + heartbeat |
| Problema de encoding em log redirecionado | `UnicodeEncodeError` / caracteres “��” | UTF‑8 em `main.py` + `chcp 65001` |
| Processo finaliza por exceção não tratada | serviço “parado” | watchdog (`iniciar.bat`) + tarefa agendada |

---

## 8) Operação no Windows (runbook rápido)

- **Instalar** (Admin): `instalar_servico.bat`
- **Remover** (Admin): `desinstalar_servico.bat`
- **Validar execução**:
  - conferir `logs/Ptytho-MonitoramentoViaweb.log` (heartbeat e timestamps)
  - conferir tabela `eventos` para eventos do dia

