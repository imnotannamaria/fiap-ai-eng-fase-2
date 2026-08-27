# Segurança, privacidade e uso responsável

## Escopo e princípio central

Este projeto usa um dataset público e anonimizado. Ele demonstra apoio à triagem, não pode diagnosticar pacientes e não deve ser conectado a prontuários reais sem avaliação institucional, jurídica e clínica.

## Riscos e controles

| Risco | Controle adotado |
|---|---|
| Falso negativo | Recall de malignos é a métrica principal; há contagem explícita de falsos negativos; revisão humana obrigatória. |
| Uso como diagnóstico final | Avisos no README, documentação e prompt da LLM: o resultado é apoio à decisão. |
| Vazamento de dados para provedor externo | A LLM é executada localmente pelo Ollama; o prompt deve usar apenas dados mínimos e sem identificadores pessoais. |
| Prompt com saída clínica inadequada | Prompt de sistema restringe diagnóstico, tratamento e invenção de informações; respostas são avaliadas por rubrica. |
| Segredos expostos | Nenhuma chave é necessária para Ollama. Caso uma API externa seja adotada no futuro, chaves devem ficar em variáveis de ambiente e nunca no Git. |
| Dependências vulneráveis | Versões são fixadas em `requirements.txt`; atualizar e revisar dependências antes de qualquer implantação. |
| Modelo degradado em outro hospital | Não há validação externa neste dataset. Uma implantação real exige validação prospectiva, monitoramento de drift e aprovação clínica. |

## Dados e logs

Os logs de experimento contêm parâmetros, métricas e timestamps, mas não devem registrar dados identificáveis de pacientes. Em produção, acesso, retenção e descarte de logs precisam seguir a política do hospital e a LGPD.
