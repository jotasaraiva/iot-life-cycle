## Ciclo de Vida IoT

O presente WebApp desenvolvido em Streamlit serve como um sistema de gestão e monitoramento de estoque dos sensores IoTs da Treevia, criado com o objetivo de captar e recordar os dados de fornecimento, envio e remanufatura dos dispositivos. Desta forma, o projeto visa o levantamento de indicadores e inteligência de dados úteis para a otimização das operações que envolvem o IoT.

### Estoque

O sistema IoT Life Cycle funciona primeiramente como uma ferramenta básica de gestão de estoque. Sendo assim a aba **Home** apresenta, na forma de um *dashboard*, os dados mais atuais do estoque cadastrado pela ferramenta. O procedimento de cadastro de estoque é feito pela aba **Cadastro**, onde os sensores podem ser registrados pelos seus códigos MAC Treevia e classificados em um de três *status* de seu ciclo de vida:

- **Estoque**: Sensor está disponível na companhia, podendo estar ou não sob análise técnica;
  - Origem: Subcategoria que determina se o sensor foi recebido de uma devolução de cliente ou de fornecedor
  - Diagnóstico: Subcategoria que determina um possível problema no sensor que o impede de ser viável para o envio
  - Lotes de Recebimento e Interno: Subcategorias para registro de lotes de sensores recebidos do fornecedor
- **Cliente**: Sensor que está sob a posse de um cliente ou está atualmente instalado em algum projeto, e;
- **Remanufatura**: Sensor que está atualmente na posse do fornecedor para que seja restaurado.
- **Descarte** Sensor que foi avariado ou deteriorado de uma forma irrecuperável, passível de descarte.

### Monitoramento

O sistema têm como objetivo observar e monitorar o ciclo de vida de cada sensor, visando mensurar o desempenho e a qualidade dos dispositivos a cada ciclo de envio. Quando um sensor é cadastrado pela página de **Cadastro**, ele será recordado na base de dados dedicado do sistema. Este banco atualmente possui duas tabelas:

- **Tabela Estoque**: Responsável por guardar os dados atuais da situação de estoque de IoTs, onde o status do sensor será atualizado a cada novo registro;
-  **Tabela Timeline**: Responsável por guardar todos os registros de cadastro de estoque, o que permite recordar toda a trajetória do ciclo de vida dos dispositivos.

Desta forma, os dados históricos recordados na Timeline são apresentados na aba **Análise**. Esta aba contém as informações devidamente tratadas para o do Ciclo de Vida dos sensores, com indicadores de desempenho e falha dos dispositivos cadastrados.