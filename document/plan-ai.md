# Plano de Implementação - Telegram Daily Briefing

## 🎯 Objetivo
Sistema automatizado que envia briefings diários de notícias sobre IA via Telegram, com foco especial em ChatGPT, Cursor e Lovable, executando na nuvem via GitHub Actions.

## 📋 Requisitos Principais
- **Horários**: 8:00, 12:00, 18:00 (horário de Brasília)
- **Formato**: Resumos curtos + links
- **Fontes**: APIs (OpenAI, Anthropic), RSS feeds (TechCrunch, VentureBeat, MIT Tech Review), web scraping
- **Foco**: Priorizar ChatGPT, Cursor, Lovable + notícias relevantes de IA geral
- **Critério**: Últimas 24 horas
- **Telegram**: Bot @TraydeNewsbot, Chat ID: <seu_chat_id>, Token: <seu_token>

## 🏗️ Arquitetura
**Padrão**: Pipeline Procedural (NewsCollector → ContentProcessor → MessageFormatter → TelegramSender)

## 🛠️ Stack Tecnológico
- **Python 3.9+**
- **Bibliotecas**: requests, feedparser, beautifulsoup4, python-telegram-bot, schedule, python-dotenv
- **Infra**: GitHub Actions (Ubuntu 22.04)
- **Storage**: Arquivo JSON local para estado

## 📁 Estrutura do Projeto
```
telegram-daily-briefing/
├── src/
│   ├── news_collector.py
│   ├── content_processor.py
│   ├── message_formatter.py
│   ├── telegram_sender.py
│   └── main.py
├── config/
│   ├── sources.json
│   └── settings.json
├── .github/workflows/
│   └── daily-briefing.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🔄 Componentes Principais

### 1. NewsCollector
- Coleta de APIs (OpenAI, Anthropic)
- Parsing de RSS feeds
- Web scraping básico
- Filtro por data (24h) e relevância

### 2. ContentProcessor
- Remove duplicatas e itens já processados
- Prioriza por keywords (ChatGPT, Cursor, Lovable > IA geral)
- Limita a 10 notícias por execução
- Estado persistido em JSON

### 3. MessageFormatter
- Formato: 📰 Título\n📝 Resumo[:150]...\n🔗 URL\n\n
- Limite de 4000 chars por mensagem
- Suporte a múltiplas mensagens

### 4. TelegramSender
- Interface com Telegram Bot API
- Retry logic e rate limiting
- Tratamento de erros

## 📅 Roadmap de Implementação

### Fase 1: Setup Base (1-2 dias)
- [ ] Criar estrutura de diretórios
- [ ] requirements.txt com dependências
- [ ] GitHub Actions workflow básico
- [ ] Arquivos de configuração

### Fase 2: Core Components (2-3 dias)
- [ ] NewsCollector com APIs básicas
- [ ] TelegramSender funcional
- [ ] main.py pipeline básico
- [ ] Testes de integração locais

### Fase 3: Fontes de Notícias (2-3 dias)
- [ ] RSS feeds (TechCrunch, VentureBeat, MIT)
- [ ] Web scraping básico
- [ ] Sistema de relevância e filtragem
- [ ] ContentProcessor completo

### Fase 4: Refinamentos (1-2 dias)
- [ ] Otimização de mensagens
- [ ] Cron jobs (8:00, 12:00, 18:00 BRT)
- [ ] Logging estruturado
- [ ] Error handling robusto

### Fase 5: Deploy (1 dia)
- [ ] Configuração de secrets no GitHub
- [ ] Deploy em produção
- [ ] Testes finais
- [ ] Documentação

## ⚠️ Riscos e Mitigações
1. **Rate Limiting**: Delays entre requests, headers realistas
2. **Mudanças de Sites**: Priorizar APIs, selectors robustos
3. **Falhas Telegram**: Retry logic, notificações de erro
4. **Dependências**: Version pinning, testes automatizados

## ✅ Critérios de Sucesso
- 5-10 notícias relevantes por dia
- 95%+ uptime das execuções
- < 30s por execução
- < 5% taxa de erro
- Código testável e documentado

## 🔐 Configuração de Segurança
- Token do Telegram: GitHub Secret `TELEGRAM_BOT_TOKEN`
- Chat ID: GitHub Secret `TELEGRAM_CHAT_ID`
- Outras chaves de API: conforme necessário

## 🚀 Próximos Passos
1. Criar estrutura base do projeto
2. Implementar pipeline principal
3. Adicionar fontes de notícias
4. Configurar agendamento
5. Deploy e testes finais
