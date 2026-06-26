# 🚀 Dashboard Web - VIAWEB Receiver Monitoring

## 📋 Descrição

Dashboard web em tempo real para monitoramento dos eventos do VIAWEB Receiver com interface moderna e atualização automática a cada 3 segundos.

## ✨ Funcionalidades

### 🎯 Monitoramento em Tempo Real
- ✅ Status do sistema (Online/Offline/Travado)
- ✅ Contadores de eventos (hoje, última hora)
- ✅ Tempo desde o último evento
- ✅ Lista completa de eventos recebidos
- ✅ Atualização automática a cada 3 segundos
- ✅ Alertas visuais quando o sistema está travado ou offline

### 📊 Visualizações
- **Cards de Status**: Informações principais em destaque
- **Tabela de Eventos**: Lista completa com todos os detalhes
- **Indicadores Visuais**: Status com cores e animações
- **Alertas**: Avisos quando há problemas

### 🎨 Interface
- Design moderno e responsivo
- Cores e animações suaves
- Interface intuitiva
- Compatível com todos os navegadores

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

As novas dependências incluem:
- `flask` - Framework web
- `flask-cors` - Suporte a CORS

### 2. Iniciar o Dashboard

**Opção 1: Usando o script batch**
```batch
iniciar_dashboard.bat
```

**Opção 2: Via linha de comando**
```bash
python web_server.py
```

### 3. Acessar o Dashboard

Abra seu navegador em:
```
http://localhost:5000
```

### 4. Visualizar em Tempo Real

O dashboard irá:
- ✅ Conectar automaticamente ao banco de dados
- ✅ Buscar o status do sistema
- ✅ Listar os últimos eventos
- ✅ Atualizar automaticamente a cada 3 segundos

## 📸 Recursos Visuais

### Status do Sistema

```
┌─────────────────────────────────┐
│ 🛡️ Status do Sistema            │
│                                 │
│  🟢 ONLINE                      │
│  Sistema operando normalmente   │
└─────────────────────────────────┘
```

### Eventos Hoje

```
┌─────────────────────────────────┐
│ 📊 Eventos Hoje                 │
│                                 │
│         150                     │
│  Total de eventos recebidos     │
└─────────────────────────────────┘
```

### Alertas

**Sistema Travado:**
```
⚠️ Sistema Travado!
Não há eventos há 10min. Verifique a conexão.
```

**Sistema Offline:**
```
❌ Sistema Offline!
O monitoramento não está ativo. Inicie o main.py.
```

## 🔧 API Endpoints

### GET /api/status
Retorna o status atual do sistema

**Resposta:**
```json
{
  "status": "success",
  "sistema_online": true,
  "travado": false,
  "tempo_sem_evento": 30.5,
  "eventos_hoje": 150,
  "eventos_ultima_hora": 25,
  "ultima_conexao": "2026-01-27T10:30:00",
  "timestamp": "2026-01-27T10:35:00"
}
```

### GET /api/eventos?limit=50
Retorna os últimos eventos

**Parâmetros:**
- `limit` (opcional): Quantidade de eventos a retornar (padrão: 50)

**Resposta:**
```json
{
  "status": "success",
  "eventos": [
    {
      "id": 123,
      "data_recepcao": "2026-01-27T10:30:00",
      "data_evento": "2026-01-27T10:30:00",
      "id_isep": "0001",
      "conta_isep": "0001",
      "codigo_evento": "1411",
      "usuario_zona": "52",
      "meio_comunicacao": "ETH",
      "equipamento": "VW16ZETH 14951039",
      "descricao": "COD. 1411 Zona 52"
    }
  ]
}
```

### GET /api/estatisticas
Retorna estatísticas gerais dos eventos

**Resposta:**
```json
{
  "status": "success",
  "total_eventos": 5000,
  "eventos_por_codigo": [...],
  "eventos_por_isep": [...],
  "eventos_por_hora": [...]
}
```

## 🎯 Uso Recomendado

### Monitoramento 24/7

1. **Inicie o monitoramento:**
   ```bash
   python main.py
   ```

2. **Em outro terminal, inicie o dashboard:**
   ```bash
   python web_server.py
   ```

3. **Acesse o dashboard no navegador:**
   ```
   http://localhost:5000
   ```

4. **Deixe aberto para monitoramento contínuo**

### Acesso Remoto

Para acessar de outros computadores na rede:

1. O servidor já está configurado para aceitar conexões externas (host='0.0.0.0')

2. Descubra seu IP:
   ```bash
   ipconfig
   ```

3. Acesse de outro computador:
   ```
   http://SEU_IP:5000
   ```

## 🔐 Segurança

- O dashboard é somente leitura (read-only)
- Não permite modificar ou deletar eventos
- Acesso local por padrão
- Para produção, considere adicionar autenticação

## 🛠️ Personalização

### Alterar Intervalo de Atualização

Edite `templates/dashboard.html`:

```javascript
const REFRESH_INTERVAL = 3000; // 3 segundos
```

### Alterar Limite de Eventos Exibidos

Edite `templates/dashboard.html`:

```javascript
const response = await fetch(`${API_URL}/api/eventos?limit=100`);
```

### Alterar Porta do Servidor

Edite `web_server.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

## 📊 Informações Exibidas

### Cards de Status
1. **Status do Sistema**: Online/Offline/Travado com indicador animado
2. **Eventos Hoje**: Total de eventos recebidos no dia
3. **Última Hora**: Eventos dos últimos 60 minutos
4. **Último Evento**: Tempo desde o último evento recebido

### Tabela de Eventos
- ID do evento
- Data/Hora de recepção
- ID ISEP
- Conta do cliente
- Código do evento
- Zona/Usuário
- Meio de comunicação (com badge colorido)
- Equipamento
- Descrição

## 🐛 Solução de Problemas

### Dashboard não carrega

**Problema:** Erro ao acessar http://localhost:5000

**Solução:**
1. Verifique se o `web_server.py` está rodando
2. Verifique se a porta 5000 está disponível
3. Tente acessar via http://127.0.0.1:5000

### Alertas de erro

**Problema:** "Erro de Conexão! Não foi possível conectar ao servidor"

**Solução:**
1. Certifique-se que `web_server.py` está executando
2. Verifique firewall/antivírus bloqueando a porta

**Problema:** "Banco de dados desconectado"

**Solução:**
1. Verifique credenciais do banco no arquivo `.env`
2. Teste conexão com o MySQL

**Problema:** "Sistema Offline"

**Solução:**
1. Inicie o monitoramento: `python main.py`
2. Aguarde alguns segundos para o dashboard atualizar

## 📝 Logs

O dashboard usa o mesmo banco de dados que o sistema principal, então todos os eventos são compartilhados em tempo real.

## 🎉 Pronto!

Agora você tem um dashboard completo para monitorar seus eventos do VIAWEB Receiver em tempo real! 🚀
