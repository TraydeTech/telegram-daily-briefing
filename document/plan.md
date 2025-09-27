# Plano de Implementação - Telegram Daily Briefing

## Fase 1 – Análise de Requisitos

### Achados / entregáveis

#### Requisitos Funcionais Explícitos:
1. Receber mensagens no Telegram sobre notícias diárias de IA
2. Cobrir novas tecnologias de IA no mercado
3. Atualizações de modelos de AI existentes
4. Foco específico em:
   - ChatGPT
   - Cursor
   - Lovable
5. Sistema deve funcionar automaticamente todo dia
6. Deve rodar na nuvem com GitHub Actions
7. Funcionar independente do status do Mac do usuário

#### Requisitos Implícitos:
1. Sistema de coleta automática de notícias de IA
2. Filtragem e relevância de conteúdo
3. Agendamento diário de mensagens
4. Integração com API do Telegram Bot
5. Gerenciamento de estado (últimas notícias enviadas)
6. Tratamento de erros e fallbacks
7. Logs de execução

#### Requisitos Não-Funcionais:
- **Disponibilidade**: Sistema deve funcionar 24/7 na nuvem
- **Confiabilidade**: Não perder execuções diárias
- **Performance**: Resposta rápida às notificações
- **Manutenibilidade**: Código limpo e documentado
- **Escalabilidade**: Capacidade de adicionar mais fontes de notícias
- **Segurança**: Proteção de tokens/API keys
- **Custo**: Uso eficiente de recursos do GitHub Actions

### Confidence: 75%

### Perguntas em aberto
1. Quais são os detalhes específicos do bot do Telegram já criado? (token, username, etc.)
2. Quais fontes de notícias de IA devem ser monitoradas? (sites, APIs, feeds RSS)
3. Em que horário do dia as mensagens devem ser enviadas?
4. Qual o formato desejado das mensagens? (resumo, links, detalhes completos)
5. Deve haver personalização por usuário ou será um broadcast geral?
6. Qual o critério de "novidade" das notícias? (últimas 24h, desde última execução)
7. Deve haver armazenamento histórico das notícias enviadas?

### Próximos passos
Aguardar respostas do usuário para as perguntas em aberto antes de prosseguir para Fase 2.

### Respostas e decisões
1. **Bot Telegram**:
   - Token: <seu_token>
   - Chat ID: <seu_chat_id>
   - Username: @TraydeNewsbot

2. **Fontes de Notícias**:
   - Sites: TechCrunch, VentureBeat, MIT Technology Review
   - APIs oficiais: OpenAI, Anthropic
   - Feeds RSS de blogs especializados
   - Aberto a sugestões melhores

3. **Horário de Envio**: 8:00, 12:00, 18:00 horário de Brasília

4. **Formato das Mensagens**: Resumos curtos + links

5. **Critério de Novidade**: Últimas 24 horas

6. **Escopo**: Foco maior em ChatGPT, Cursor e Lovable + notícias relevantes de IA em geral

## Fase 2 – Contexto do Sistema

### Achados / entregáveis

#### Estrutura Atual do Projeto
- **Status**: Projeto recém-inicializado com apenas repositório Git vazio
- **Tecnologias**: Nenhuma definida ainda
- **Estrutura**: Necessário criar estrutura completa do projeto

#### Sistemas Externos e Pontos de Integração

1. **Telegram Bot API**
   - Endpoint: https://api.telegram.org/bot{token}/
   - Método principal: sendMessage
   - Chat ID: 7842820997 (destinatário único)

2. **Fontes de Dados de Notícias**
   - **APIs Oficiais**:
     - OpenAI API (para atualizações do ChatGPT)
     - Anthropic API (para Claude/IA concorrente)
   - **Sites de Notícias**:
     - TechCrunch (techcrunch.com)
     - VentureBeat (venturebeat.com)
     - MIT Technology Review (technologyreview.com)
   - **Feeds RSS**: Blogs especializados em IA

3. **GitHub Actions** (Infraestrutura de Execução)
   - Scheduled workflows (cron jobs)
   - Secrets management para tokens
   - Runtime: Ubuntu latest

4. **Armazenamento**
   - GitHub repository (código fonte)
   - Possível: arquivo JSON local para estado (últimas notícias)

#### Limites e Responsabilidades

**Sistema Telegram Daily Briefing**:
- ✅ Coleta automática de notícias de IA
- ✅ Filtragem por relevância e novidade (24h)
- ✅ Formatação de mensagens (resumo + link)
- ✅ Envio agendado via Telegram
- ✅ Foco em ChatGPT, Cursor, Lovable + IA geral

**Não Responsabilidades**:
- ❌ Moderação de conteúdo
- ❌ Interação bidirecional com usuários
- ❌ Armazenamento persistente em banco de dados
- ❌ Análise avançada de sentimento

#### Diagrama de Contexto (Alto Nível)

```
[GitHub Actions Scheduler]
        ↓
[News Collector Service]
        ↓
[APIs] ←→ [RSS Feeds] ←→ [Web Scraping]
        ↓
[Content Filter & Formatter]
        ↓
[Telegram Bot API]
        ↓
[User Chat (ID: 7842820997)]
```

### Confidence: 85%

### Perguntas em aberto
Nenhuma pergunta crítica restante após esclarecimentos da Fase 1.

### Próximos passos
Prosseguir para Fase 3 - Design da Arquitetura.

### Respostas e decisões
*Aguardando decisões da Fase 3 sobre padrões arquiteturais*

## Fase 3 – Design da Arquitetura

### Achados / entregáveis

#### Padrões Arquiteturais Considerados

**Opção 1: Arquitetura de Pipeline/Script Procedural**
- **Descrição**: Script sequencial que executa etapas em ordem: coleta → filtro → formatação → envio
- **Vantagens**:
  - Simplicidade máxima para implementação
  - Fácil debug e manutenção
  - Adequado para execução agendada (batch processing)
  - Baixo overhead computacional
- **Desvantagens**:
  - Dificuldade para adicionar novas fontes sem refatorar
  - Monolítico - falha em uma etapa para tudo
  - Pouca reutilização de componentes
- **Adequação**: Excelente para este projeto simples e específico

**Opção 2: Arquitetura de Microserviços Simples**
- **Descrição**: Módulos separados para cada responsabilidade (collector, filter, sender)
- **Vantagens**:
  - Modularidade e reutilização
  - Fácil adicionar novas fontes
  - Testabilidade individual
  - Escalabilidade horizontal
- **Desvantagens**:
  - Overhead desnecessário para projeto pequeno
  - Complexidade maior de deployment
  - Coordenação entre módulos
  - Mais arquivos e configuração
- **Adequação**: Exagerado para requisitos atuais

**Opção 3: Arquitetura Orientada a Eventos**
- **Descrição**: Sistema baseado em eventos com publishers/subscribers
- **Vantagens**:
  - Desacoplamento entre componentes
  - Fácil extensão e modificação
  - Suporte a processamento assíncrono
  - Boa para integrações futuras
- **Desvantagens**:
  - Complexidade alta para caso de uso simples
  - Overhead de infraestrutura de eventos
  - Curva de aprendizado maior
  - Não necessário para execução síncrona
- **Adequação**: Muito complexo para necessidades atuais

#### Recomendação Arquitetural
**🏆 Opção 1: Arquitetura de Pipeline/Script Procedural**

**Justificativa**:
- Requisitos são bem definidos e estáveis
- Execução sequencial e determinística
- Simplicidade de manutenção em ambiente GitHub Actions
- Adequado para equipe pequena/single developer
- Foco em confiabilidade sobre flexibilidade futura

#### Componentes Centrais e Responsabilidades

1. **NewsCollector**
   - Responsável por buscar notícias de todas as fontes
   - Gerencia diferentes tipos de fonte (API, RSS, web scraping)
   - Filtra por data (últimas 24h) e relevância

2. **ContentProcessor**
   - Processa e filtra conteúdo coletado
   - Remove duplicatas e conteúdo irrelevante
   - Prioriza notícias sobre ChatGPT, Cursor, Lovable

3. **MessageFormatter**
   - Formata mensagens no padrão: resumo curto + link
   - Limita tamanho das mensagens
   - Trata caracteres especiais do Telegram

4. **TelegramSender**
   - Interface com Telegram Bot API
   - Gerencia rate limiting e erros
   - Envia mensagens para chat específico

#### Interfaces/Contratos Entre Componentes

```python
# Exemplo de contratos (pseudocódigo)
class NewsItem:
    title: str
    summary: str
    url: str
    source: str
    published_at: datetime
    relevance_score: float

class NewsCollector:
    def collect() -> List[NewsItem]

class ContentProcessor:
    def process(news_items: List[NewsItem]) -> List[NewsItem]

class MessageFormatter:
    def format(news_items: List[NewsItem]) -> List[str]

class TelegramSender:
    def send(messages: List[str]) -> bool
```

#### Preocupações Transversais

- **Logging**: Uso de logging estruturado para debugging
- **Error Handling**: Graceful degradation, retry logic
- **Configuration**: Environment variables para tokens/secrets
- **State Management**: Arquivo JSON para tracking de últimas execuções
- **Security**: Proteção de API tokens via GitHub Secrets

### Confidence: 90%

### Perguntas em aberto
**Decisão Arquitetural**: Você concorda com a recomendação da Arquitetura de Pipeline/Script Procedural, ou prefere avaliar melhor as outras opções?

### Próximos passos
Após decisão sobre arquitetura, prosseguir para Fase 4 - Especificação Técnica.

### Respostas e decisões
**✅ Decisão Arquitetural**: Usuário concordou com a recomendação da Arquitetura de Pipeline/Script Procedural.

## Fase 4 – Especificação Técnica

### Achados / entregáveis

#### Tecnologias Concretas Selecionadas

**Linguagem de Programação: Python 3.9+**
- **Razão**: Excelente suporte para APIs HTTP, processamento de dados, bibliotecas de RSS e web scraping
- **Alternativas consideradas**: Node.js (boa para APIs), Go (performance), mas Python tem melhor ecossistema para IA/news scraping
- **Suporte GitHub Actions**: Nativo e eficiente

**Bibliotecas Principais**:
- **requests** (2.31.0+): HTTP client para APIs e web scraping
- **feedparser** (6.0.10+): Parsing de feeds RSS/Atom
- **beautifulsoup4** (4.12.0+): HTML parsing para web scraping
- **python-telegram-bot** (20.7+): Interface oficial com Telegram Bot API
- **schedule** (1.2.0+): Agendamento local (útil para testes)
- **python-dotenv** (1.0.0+): Gerenciamento de variáveis de ambiente

**Infraestrutura**:
- **GitHub Actions**: Ubuntu 22.04 LTS runner
- **Secrets Management**: GitHub Secrets para tokens
- **Storage**: Arquivo JSON local para estado das últimas notícias

#### Roadmap de Implementação em Fases

**Fase 1: Setup e Estrutura Base** (1-2 dias)
- Criar estrutura de diretórios
- Configurar requirements.txt e dependências
- Setup GitHub Actions workflow básico
- Criar arquivos de configuração

**Fase 2: Core Components** (2-3 dias)
- Implementar NewsCollector com APIs básicas (OpenAI, Anthropic)
- Criar TelegramSender funcional
- Testes básicos de integração

**Fase 3: Fontes de Notícias** (2-3 dias)
- Adicionar RSS feeds (TechCrunch, VentureBeat, etc.)
- Implementar web scraping básico
- Sistema de relevância e filtragem

**Fase 4: Refinamentos e Agendamento** (1-2 dias)
- Otimizar formato de mensagens
- Configurar cron jobs (8:00, 12:00, 18:00 BRT)
- Logging e error handling
- Testes finais

**Fase 5: Deploy e Monitoramento** (1 dia)
- Deploy em produção
- Configurar monitoring básico
- Documentação final

#### Riscos Técnicos Identificados

**Risco 1: Rate Limiting de APIs**
- **Descrição**: Sites/APIs podem bloquear requests excessivos
- **Mitigação**: Implementar delays, caching, headers realistas
- **Impacto**: Médio
- **Probabilidade**: Alta

**Risco 2: Mudanças em Estrutura de Sites**
- **Descrição**: Web scraping quebra com mudanças de layout
- **Mitigação**: Usar APIs quando possível, selectors robustos, monitoring
- **Impacto**: Médio
- **Probabilidade**: Média

**Risco 3: Falhas na Telegram API**
- **Descrição**: Rate limiting ou indisponibilidade temporária
- **Mitigação**: Retry logic, fallback, notificações de erro
- **Impacto**: Baixo
- **Probabilidade**: Baixa

**Risco 4: Dependências Externas**
- **Descrição**: Quebra de compatibilidade em bibliotecas
- **Mitigação**: Version pinning, testes automatizados, CI/CD
- **Impacto**: Baixo
- **Probabilidade**: Baixa

#### Especificações Detalhadas dos Componentes

**1. NewsCollector**
```python
class NewsCollector:
    def __init__(self, config: Dict):
        self.sources = config['sources']
        self.keywords = ['ChatGPT', 'Cursor', 'Lovable', 'AI', 'artificial intelligence']
        self.max_age_hours = 24

    def collect_all(self) -> List[NewsItem]:
        all_news = []
        all_news.extend(self._collect_from_apis())
        all_news.extend(self._collect_from_rss())
        all_news.extend(self._collect_from_web())
        return self._filter_by_date_and_relevance(all_news)
```

**2. ContentProcessor**
```python
class ContentProcessor:
    def __init__(self, state_file: str = 'news_state.json'):
        self.state_file = state_file
        self.processed_urls = self._load_processed_urls()

    def process(self, news_items: List[NewsItem]) -> List[NewsItem]:
        # Remove duplicatas e já processadas
        unique_items = self._remove_duplicates(news_items)
        # Prioriza por relevância (ChatGPT, Cursor, Lovable > IA geral)
        prioritized = self._prioritize_by_keywords(unique_items)
        # Limita quantidade por execução
        return prioritized[:10]  # Máximo 10 notícias por vez
```

**3. MessageFormatter**
```python
class MessageFormatter:
    def __init__(self, max_length: int = 4000):
        self.max_length = max_length

    def format_messages(self, news_items: List[NewsItem]) -> List[str]:
        messages = []
        current_message = ""

        for item in news_items:
            formatted_item = self._format_single_item(item)

            # Verifica se cabe na mensagem atual
            if len(current_message + formatted_item) > self.max_length:
                if current_message:
                    messages.append(current_message.strip())
                current_message = formatted_item
            else:
                current_message += formatted_item

        if current_message:
            messages.append(current_message.strip())

        return messages

    def _format_single_item(self, item: NewsItem) -> str:
        return f"📰 {item.title}\n📝 {item.summary[:150]}...\n🔗 {item.url}\n\n"
```

**4. TelegramSender**
```python
class TelegramSender:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_messages(self, messages: List[str]) -> bool:
        success = True
        for message in messages:
            if not self._send_single_message(message):
                success = False
                logger.error(f"Failed to send message: {message[:100]}...")
        return success

    def _send_single_message(self, text: str) -> bool:
        # Implementar com retry logic e rate limiting
        pass
```

#### Critérios de Sucesso Técnico

- **Funcionalidade**: Sistema envia pelo menos 5-10 notícias relevantes por dia
- **Confiabilidade**: 95%+ de uptime das execuções agendadas
- **Performance**: Resposta em < 30 segundos por execução
- **Qualidade**: Taxa de erro < 5% nas mensagens enviadas
- **Manutenibilidade**: Código limpo, documentado, testável

### Confidence: 95%

### Perguntas em aberto
Nenhuma - especificações técnicas completas definidas.

### Próximos passos
Prosseguir para Fase 5 - Decisão de Transição.

### Respostas e decisões
*Especificações técnicas finalizadas - pronto para transição*

## Fase 5 – Decisão de Transição

### Achados / entregáveis

#### Resumo da Recomendação Arquitetural
**Padrão**: Arquitetura de Pipeline/Script Procedural
**Stack**: Python 3.9+, GitHub Actions, Telegram Bot API
**Componentes**: NewsCollector → ContentProcessor → MessageFormatter → TelegramSender

#### Roadmap de Implementação
1. **Setup Base** (1-2 dias): Estrutura, dependências, GitHub Actions
2. **Core Components** (2-3 dias): APIs básicas, Telegram integration
3. **Fontes de Notícias** (2-3 dias): RSS feeds, web scraping, filtros
4. **Refinamentos** (1-2 dias): Agendamento, logging, testes
5. **Deploy** (1 dia): Produção e monitoramento

**Tempo Total Estimado**: 7-11 dias de desenvolvimento

### Confidence: 95%

#### ✅ Critérios de Transição Atendidos:
- ✅ Requisitos funcionais bem definidos e validados
- ✅ Arquitetura escolhida e justificada
- ✅ Tecnologias selecionadas com rationale
- ✅ Riscos identificados e mitigados
- ✅ Roadmap detalhado de implementação
- ✅ Confidence ≥ 90%

### Próximos passos
Criar plan-ai.md e iniciar implementação no modo Agent Engineer.

### Respostas e decisões
*Transição autorizada - confidence suficiente para implementação*
