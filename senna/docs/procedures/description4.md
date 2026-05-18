# Nota de Atualização: Inclusão do settings.toml
Data: 18 de maio de 2026
Tipo: Adição de Arquivo de Configuração

## O que foi feito
- **Inclusão do arquivo padrão `settings.toml`**: Adicionamos o arquivo na raiz do repositório (`senna/settings.toml`), contendo parâmetros essenciais de timeout para os browsers, estrutura de caminhos para os arquivos locais e a estrutura de configuração dos logs (rotações).
- **Validação Pós-Inclusão**: 
  - Ao executar os testes na `test_config.py`, obtivemos novamente uma falha em tempo de coleção apontando o `MissingCredentialError`. Este comportamento assegura que, embora o `settings.toml` tenha sido carregado adequadamente, o mecanismo Fail-Fast implementado no `config.py` agiu corretamente ao perceber a ausência das variáveis obrigatórias sensíveis que só seriam lidas do `.env`.
  - A formatação via linter não registrou problemas de compliance para as alterações.

## Justificativa
Desacoplar a base de metadados padronizados do robô em um arquivo centralizado que pode ser versionado com total segurança. A falha de injeção de ambiente corrobora o sucesso do modelo restritivo implementado na refatoração da `config`.
