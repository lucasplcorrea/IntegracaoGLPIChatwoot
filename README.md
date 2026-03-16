# Integração Chatwoot — Histórico Unificado de Contatos

Sistema complementar ao Chatwoot que consolida e exibe todas as mensagens de conversas passadas de um contato em uma interface unificada, rodando embarcada dentro do próprio painel de atendimento (Dashboard App) do Chatwoot.

## Arquitetura

O projeto é dividido em três camadas:
- **Backend**: API construída em Python (FastAPI). Responsável por servir os dados do histórico, ouvir *webhooks* do Chatwoot para sincronização automática e consumir a API nativa do Chatwoot puxando o histórico completo contornando paginações e iterando por anexos de mídia.
- **Dashboard**: PWA construído em React (Vite). Ele roda dentro de um iframe no Chatwoot ouvindo comunicações *postMessage* nativas para descobrir os IDs corretos do contato e conversa sem exigir preenchimento manual.
- **Banco de Dados**: PostgreSQL, guardando snapshots sincronizados das conversas e mensagens para pesquisa instantânea.

## Instalação com Docker (Recomendado) 🐳

Preparamos o repositório para ser rodado via Contêineres. Se você for subir o projeto em nuvem, este é o melhor cenário.

1. **Clone e configure o ambiente:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd IntegracaoGLPIChatwoot
   ```

2. **Crie os arquivos `.env`**:
   O Docker Compose irá procurar as variáveis no backend. Crie o arquivo dele:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Preencha o seu `backend/.env` com os relatórios obrigatórios:
   - `CHATWOOT_BASE_URL` — (ex: `https://chatwoot.suaempresa.com`)
   - `CHATWOOT_ACCOUNT_ID` — (ex: `1`)
   - `CHATWOOT_API_TOKEN` — Token válido do perfil
   - `CHATWOOT_WEBHOOK_SECRET` — (Chave de autenticação do Webhook)

3. **Configuração de Frontend (Vite)**
   Para o container de Dashboard funcionar localmente, ele procura por padrão na build a URL local do host. Caso esteja subindo em subdomínio de nuvem próprio, configure o `dashboard/.env` contendo `VITE_API_BASE_URL`.

4. **Inicie o Docker Compose**:
   Na raiz do repositório, rode:
   ```bash
   docker-compose up -d --build
   ```

Isso subirá os contêineres:
- `chatwoot_history_db`: PostgreSQL rodando na 5433 host.
- `chatwoot_history_backend`: API Python na porta 8000 host.
- `chatwoot_history_dashboard`: Interface Web/Vite na porta 3000 host através do Nginx.

## Integração com o Chatwoot

Após os pacotes e portas em execução:

### 1. Webhook Automatizado do Chatwoot
Para que o sistema atualize o histórico sempre que seu atendente marcar uma conversa como resolvida, vá nas configurações de Webhooks do Chatwoot:
- **URL**: `http://SEU_IP_OU_DOMINIO:8000/api/v1/webhooks/chatwoot`
- **Events**: Ative `conversation_status_changed` (e similares que desejar).

### 2. Configurar o Dashboard App dentro do Chatwoot
Em **Settings → Integrations → Dashboard Apps**, adicione:
- **Nome**: Histórico do Cliente (Ou "Histórico Completo")
- **URL**:  `http://SEU_IP_OU_DOMINIO:3000/`

Sempre que a integração for acessada via barra lateral, ela receberá e exibirá contextualmente todo o histórico de mensagens! 

## DockerHub 📦

As imagens oficiais estão disponíveis no DockerHub para facilitar o deploy sem necessidade de build local:

- **Backend**: `lucasplcorrea/chatwoot-history-backend`
- **Dashboard**: `lucasplcorrea/chatwoot-history-dashboard`

### Usando imagens prontas (Docker Compose)

Se não quiser clonar o código, você pode usar apenas o `docker-compose.yaml` apontando para as imagens:

```yaml
services:
  backend:
    image: lucasplcorrea/chatwoot-history-backend:latest
    # ... resto das configurações
  dashboard:
    image: lucasplcorrea/chatwoot-history-dashboard:latest
    # ... resto das configurações
```

---

## Limpeza Extra de Repositório

Arquivos de `.env`, cache Node/Python (`node_modules`, `.venv`), assim como lixo de dumps de rede `.har` estão contidos na malha do `.gitignore` para facilitar esteira CI/CD para seu projeto no Dockerhub ou repositórios Git públicos/privados de forma limpa.
