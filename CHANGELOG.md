## v0.2.0 (2025-02-09)

### Feat

- **emblemas**: foi adicionado emblemas de eventos do sistema
- **instruções**: Adiciona CompoundInstruction para execução sequencial de instruções
- **instruções**: Adiciona IfInstruction para avaliação condicional
- **instruções**: Adiciona IndicatorInstruction para cálculo de indicadores de mercado
- **instruções**: Adiciona classe base abstrata Instruction
- **instruções**: Adiciona OperationInstruction para execução segura de operações
- **instruções**: Adiciona TradeInstruction para registrar operações de trade
- **instructions**: Adiciona WaitInstruction para pausar a execução
- **context**: Adiciona classe Context para gerenciamento de variáveis de execução
- **safe-evaluator**: Implementa avaliação e execução seguras de expressões DSL
- **dsl**: Adiciona DSLError para tratamento de erros na DSL
- **interpreter**: Implementa DSLInterpreter para execução de estratégias DSL
- **market-data**: Implementa interface e provedor de dados via Binance API
- **parser**: Implementa DSLParser para converter instruções DSL em CompoundInstruction
- **indicators**: Implementa funções de indicadores técnicos
- **validator**: Implementa StrategyValidator para validar estratégias DSL

## v0.1.0 (2025-02-02)

### Feat

- **add-core-pkg**: ini core developer
- **poetry.toml**: add local env
