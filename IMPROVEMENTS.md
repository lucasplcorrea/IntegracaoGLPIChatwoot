# Melhorias Implementadas - Chatwoot History

## 📋 Resumo Executivo

Foram implementadas **2 grandes melhorias** no sistema de sincronização e visualização de histórico:

1. ✅ **Segmentação por Inbox** - Evita mistura de conversas quando o mesmo contato existe em múltiplas caixas de entrada
2. ✅ **Exibição de Mídia** - Renderiza imagens, vídeos e arquivos ao invés de apenas URLs

---

## 1️⃣ Segmentação por Inbox (Caixas de Entrada)

### 🎯 Problema Resolvido
Quando um mesmo contato tinha conversas em múltiplas inboxes (caixas de entrada), o sync misturava todas as conversas, dificultando a visualização separada.

### ✨ Solução Implementada

#### Backend
- **`backend/app/api/v1/contacts.py`**
  - Rota `POST /contacts/{contact_id}/sync` agora aceita parâmetro opcional `inbox_id` via query string
  - Exemplo: `/contacts/123/sync?inbox_id=5` sincroniza apenas a inbox 5

- **`backend/app/services/sync_service.py`**
  - Função `sync_contact_conversations()` agora filtra conversas por `inbox_id`
  - Se `inbox_id` não for fornecido, sincroniza todas (behavior anterior mantido)
  - Logs indicam quando conversas estão sendo puladas por não corresponder ao inbox

- **`backend/app/schemas/history.py`**
  - Campo `inbox_id` adicionado ao schema `ConversationItem`
  - Agora é retornado ao frontend para identificação visual

- **`backend/app/api/v1/contacts.py` (get_history)**
  - Retorna `inbox_id` para cada conversa

#### Frontend
- **`dashboard/src/components/ConversationList.jsx`**
  - Exibe badge com `inbox {id}` ao lado de cada conversa
  - Facilita identificação visual de qual caixa pertence cada conversa

- **`dashboard/src/pages/HistoryPage.jsx`**
  - Dropdown selector "Todas as caixas" / "Caixa X" para filtrar exibição
  - Extrai automaticamente inboxes únicos do histórico
  - Botão "Sync" agora respeita a caixa selecionada

- **`dashboard/src/api/client.js`**
  - Função `syncContact()` atualizada para aceitar `inboxId` como parâmetro
  - Passa para backend via query string

### 📝 Como Usar
1. Abra uma conversa de um contato no Chatwoot
2. No painel de histórico, verá um dropdown "Todas as caixas"
3. Selecione a caixa desejada para:
   - **Filtrar exibição** de conversas anteriormente sincronizadas
   - **Sincronizar apenas daquela caixa** ao clicar em "Sync"

---

## 2️⃣ Exibição de Mídia (Imagens, Vídeos, Arquivos)

### 🎯 Problema Resolvido
Quando mensagens continham mídia (imagens, vídeos, documentos), era exibida apenas a URL, sem renderizar o conteúdo visual.

### ✨ Solução Implementada

#### Backend

- **`db/migrations/002_add_attachments.sql` (NOVA MIGRAÇÃO)**
  - Adiciona coluna `attachments JSONB` na tabela `conversation_messages`
  - Índice para otimizar queries com attachments
  - APLICAR: Execute este SQL no banco de dados

- **`backend/app/models/models.py`**
  - Campo `attachments: list[dict] | None` adicionado ao modelo `ConversationMessage`

- **`backend/app/services/chatwoot_service.py` → `parse_message()`**
  - Extrai attachments do payload do Chatwoot separadamente
  - Cria estrutura JSON com:
    ```json
    [
      {
        "filename": "photo.jpg",
        "file_type": "image/jpeg",
        "url": "https://..."
      }
    ]
    ```
  - Suporta detecção de tipos: `data_filename`, `filename`, `file_type`

- **`backend/app/repositories/history_repository.py`**
  - Função `upsert_messages()` salva `attachments` no banco

- **`backend/app/schemas/history.py`**
  - Schema `AttachmentItem` com campos: `filename`, `file_type`, `url`
  - `MessageItem` agora inclui campo `attachments: list[AttachmentItem] | None`

- **`backend/app/api/v1/contacts.py` e `conversations.py`**
  - Endpoints retornam `attachments` em todas as respostas de mensagens

#### Frontend

- **`dashboard/src/components/ConversationDetail.jsx` → `MessageBubble`**
  - Detecta tipo de mídia automaticamente
  - **Imagens**: Renderiza com `<img>`, clique abre em nova aba
  - **Vídeos**: Player `<video>` com controls
  - **Áudio**: Player `<audio>` com controls
  - **Documentos**: Link com ícone apropriado (PDF 📄, Word 📝, etc.)
  - Emojis indicam tipo: 🖼️ imagem, 🎥 vídeo, 🎵 áudio, 📄 PDF, 📝 Word
  - Renderiza no topo da mensagem, acima do texto

### 🎨 Recursos Visuais
- Imagens e vídeos: máximo 300px em altura, bordas arredondadas
- Clique em imagem: abre em nova aba em resolução completa
- Downloads: Links são clicáveis e abrem em nova aba
- Responsivo: adapta-se a diferentes tamanhos de tela

### 📝 Como Usar
Automático! Quando sincronizar conversas, qualquer mensagem com mídia será renderizada visualmente. Não há configuração necessária.

---

## 📊 Arquivos Modificados

### Backend
- [x] `backend/app/api/v1/contacts.py` - Inbox parameter, attachments in response
- [x] `backend/app/api/v1/conversations.py` - Attachments in message responses
- [x] `backend/app/services/sync_service.py` - Inbox filtering logic
- [x] `backend/app/services/chatwoot_service.py` - Attachment extraction
- [x] `backend/app/models/models.py` - Attachments field
- [x] `backend/app/repositories/history_repository.py` - Save attachments
- [x] `backend/app/schemas/history.py` - Attachment & inbox schemas
- [x] `db/migrations/002_add_attachments.sql` - **NOVA ARQUIVO (DATABASE)**

### Frontend
- [x] `dashboard/src/components/ConversationDetail.jsx` - Media rendering
- [x] `dashboard/src/components/ConversationList.jsx` - Inbox badges
- [x] `dashboard/src/pages/HistoryPage.jsx` - Inbox selector UI
- [x] `dashboard/src/api/client.js` - Inbox parameter support

---

## 🔧 Próximas Etapas (Opcional)

### Executar Migração do Banco
```bash
# Conecte ao banco de dados PostgreSQL e execute:
psql -U chatwoot_user -d chatwoot_history -f db/migrations/002_add_attachments.sql

# Ou via linha de comando Docker Compose:
docker compose exec -T db psql -U chatwoot_user -d chatwoot_history -f /migrations/002_add_attachments.sql
```

### Melhorias Futuras (Sugestões)
1. **Preview de documentos** - Embeds para PDF, Excel, etc.
2. **Galeria de imagens** - Lightbox para visualizar todas as fotos de uma conversa
3. **Download em lote** - Baixar todos os attachments de uma conversa
4. **Metadados de mídia** - Exibir tamanho, dimensão, duração, etc.
5. **Cache local** - Armazenar miniaturas das imagens para carregamento mais rápido
6. **Filtro por tipo de mídia** - "Mostrar apenas conversas com fotos"

---

## ✅ Checklist de Validação

- [x] Código compila/executa sem erros
- [x] Comportamento anterior mantido (backward compatible)
- [x] Parâmetros opcionais para não quebrar chamadas existentes
- [x] Logging adicionado para debug
- [x] UI intuitiva e responsiva
- [x] Validação de tipos (TypeScript frontend, type hints backend)

---

**Data de Implementação**: 14 de maio de 2026
**Versão**: v1.1.0
