# Nota de Atualização: Implementação da Fábrica de Navegador (BrowserFactory)
Data: 18 de maio de 2026
Tipo: Criação de Utilitário Arquitetural (Utils)

## O que foi feito
- **Criação do utilitário `senna/utils/browser_factory.py`**:
  - **Instância Singleton**: Disponibilizamos a instância central `browser_factory` para importação e uso padronizados no projeto.
  - **Compartilhamento de Processo**: O Playwright e um único processo de navegador Chromium são instanciados e compartilhados de forma transparente sob demanda, economizando memória e recursos do sistema operacional.
  - **Isolamento de Contexto por Sistema (RF-08)**: Cada sistema-alvo (como `servicos_ti`, `aghux`, etc.) possui seu próprio `BrowserContext` estritamente isolado. Isso assegura que cookies, credenciais, localStorage e sessões ativas nunca vazem ou entrem em conflito entre diferentes automações.
  - **Parametrização Dinâmica**: Os limites de timeout padrão (`browser.timeout`) e tempo limite de navegação (`browser.navigation_timeout`) são buscados de forma dinâmica na classe `Config` (com fallbacks seguros de 30s e 60s, respectivamente).
  - **Resiliência e Desligamento Inteligente**:
    - Erros internos na inicialização do browser disparam exceções tipadas do core (`BrowserError`).
    - Fechamentos de contexto individuais são robustos a falhas silenciosas de I/O.
    - O processo do navegador é desligado automaticamente se todos os contextos forem encerrados (`_shutdown_if_idle`), liberando recursos do sistema.
    - O método público `close_all()` é disponibilizado para encerramento total das sessões ativas no teardown da aplicação.
- **Validação de Conformidade**:
  - O código foi inspecionado e formatado pelo Ruff, apresentando **100% de sucesso (zero erros)**.
  - A suíte de testes de configuração foi executada e confirmou que a introdução do arquivo não causou efeitos colaterais e a base continua perfeitamente estável.

## Justificativa
Garantir o isolamento de sessões exigido pelo requisito de segurança (RF-08) e pela robustez arquitetural do Senna, otimizando o consumo de CPU e memória ao compartilhar uma única instância do Chromium de forma controlada e resiliente.
