# Escalabilidade automática (template Kubernetes)

Estes manifestos configuram uma implantação futura em Kubernetes. Eles não foram aplicados em nenhum provedor de nuvem e, portanto, não geram custo. A API começa com duas réplicas e o HPA ajusta entre 2 e 10 de acordo com CPU média de 70%.

Para usar em um cluster que já tenha Metrics Server e uma imagem publicada:

```bash
kubectl apply -f infra/kubernetes/
```

Antes disso, troque `IMAGE_PLACEHOLDER` pelo endereço da imagem do projeto e revise as configurações de segurança do ambiente hospitalar.
