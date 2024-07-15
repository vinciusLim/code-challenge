# Documentação do Desafio de Código Técnico da Indicium

### Introdução

O projeto abrange todas as etapas de um processo ETL (Extração, Transformação e Carga), desde a configuração inicial do banco de dados Northwind utilizando Docker para executar arquivos .sql, até o agendamento e monitoramento das tarefas de carregamento de dados, com Meltano como ferramenta de ETL e Airflow para o agendamento das tarefas.

### Configuração do Banco de dados "Northwind"

O banco de dados Northwind pode ser configurado  usando o Docker. Inicie o Docker com o comando `docker-compose up` e o banco de dados será carregado automaticamente a partir do arquivo `northwind.sql`. Para gerenciar o banco de dados, utilize o pgAdmin, acessível em um navegador web na porta 5432, com as credenciais padrão `postgres` e `password`. O banco de dados possui 13 tabelas.


![Imagem do PostgreSQL](imagens/image.png)

## Iniciando o Projeto de Carregamento de Dados com Meltano

O Meltano é uma ferramenta poderosa para extrair, transformar e carregar dados. Para iniciar um projeto Meltano, utilize o comando meltano init meu_projeto. O projeto inclui um processo ETL completo, que envolve a extração de dados de duas fontes externas (um arquivo CSV e um banco de dados PostgreSQL) e o carregamento desses dados em um banco de dados interno denominado "banco_destino". Os plugins do tipo tap capturam os dados de determinada fonte, enquanto os plugins do tipo target enviam os dados para o destino. As instruções do projeto meltano ficam salvas no arquivo `meltano.yml`.

## Transferência de CSV Externo para CSV Local

O primeiro passo envolve a consolidação de arquivos CSV de detalhes de pedidos locais em um único arquivo CSV. Para isso, é necessário criar um job, que será executado pelo Airflow, utilizando os plugins `tap-csv-tipo1` e `target-csv-tipo1`.

### Comando

```bash
meltano job add tap-csv-to-target-csv --tasks "tap-csv-tipo1 target-csv-tipo1"
```

### Configurações

#### `tap-csv-tipo1`

```yaml
- name: tap-csv-tipo1
  inherit_from: tap-csv
  variant: meltanolabs
  pip_url: git+https://github.com/MeltanoLabs/tap-csv.git
  config:
    files:
      - entity: order_details
        path: ../data
        keys:
          - order_id
```

#### `target-csv-tipo1`

```yaml
- name: target-csv-tipo1
  inherit_from: target-csv
  variant: meltanolabs
  pip_url: git+https://github.com/MeltanoLabs/target-csv.git
  config:
    file_naming_scheme: data/csv/{datestamp}/dados.csv
```

## Transferência de Banco de Dados para CSV Local

O segundo passo consiste na extração de dados de um banco de dados local e sua exportação para arquivos CSV em um diretório local. Este processo utiliza os plugins `tap-postgres-tipo1` e `target-csv-tipo2`.

### Comando

```bash
meltano job add tap-postgres-to-target-csv --tasks "tap-postgres-tipo1 target-csv-tipo2"
```

### Configurações

#### `tap-postgres-tipo1`

```yaml
- name: tap-postgres-tipo1
  inherit_from: tap-postgres
  variant: meltanolabs
  pip_url: git+https://github.com/MeltanoLabs/tap-postgres.git
  config:
    sqlalchemy_url: postgresql://northwind_user:thewindisblowing@localhost:5433/northwind
    filter_schemas: [public]
```

#### `target-csv-tipo2`

```yaml
- name: target-csv-tipo2
  inherit_from: target-csv
  variant: meltanolabs
  pip_url: git+https://github.com/MeltanoLabs/target-csv.git
  config:
    validate_records: false
    add_record_metadata: false
    file_naming_scheme: data/postgres/{stream_name}/{datestamp}/dados.csv
    default_target_schema: public
    default_target_table: dados_table
```

## Transferência de CSV Local para Banco de Dados Destino

O último passo envolve a importação de arquivos CSV locais para o banco de dados "banco_destino". Para isso, são utilizados os plugins `tap-csv-tipo2` e `target-postgres-tipo1`.

### Comando

```bash
meltano job add tap-csv-to-target-postgres --tasks "tap-csv-tipo2 target-postgres-tipo1"
```

### Configurações

#### `tap-csv-tipo2`

```yaml
- name: tap-csv-tipo2
  inherit_from: tap-csv
  variant: meltanolabs
  pip_url: git+https://github.com/MeltanoLabs/tap-csv.git
  config:
    files:
      - entity: order_details
        path: data/csv/2024-07-11/dados.csv
        keys: [order_id, product_id]
      - entity: categories
        path: data/postgres/public-categories/2024-07-11/dados.csv
        keys: [category_id]
      ... (outras entidades)
```

#### `target-postgres-tipo1`

```yaml
- name: target-postgres-tipo1
  inherit_from: target-postgres
  variant: meltanolabs
  pip_url: meltanolabs-target-postgres
  config:
    sqlalchemy_url: postgresql://postgres:1234@localhost:5432/banco_destino
    default_target_schema: public
    default_target_table: dados_table
    add_record_metadata: false
    activate_version: false
```

## Agendador de fluxo com o Airflow

Utilizando Airflow, é possível agendar a execução dos jobs tap_csv_to_target_csv_task e tap_postgres_to_target_csv_task simultaneamente, responsáveis por carregar dados externos para o diretório local do projeto Meltano (/meu_meltano/data/). Após a conclusão desses jobs, o job tap_csv_to_target_postgres_task carrega esses dados locais para o banco de dados "banco_destino". O Airflow roda localmente, registrando as execuções e a qualidade dos processos, além de exibir um gráfico que mostra a ordem de execução dos jobs e se eles forem executados corretamente.

![Gráfico de Qualidade do Airflow](imagens/image%20copy.png)
![Gráfico de Ordem de Execução do Airflow](imagens/image%20copy%202.png)

## Consulta SQL

A consulta SQL abaixo permite visualizar pedidos com valor bruto superior a 2000 ordenado pelo preço do menor para o maior, salvando o resultado na pasta "data":

```sql
SELECT *
FROM (
    SELECT
        o.order_id,
        od.product_id,
        (CAST(od.unit_price AS NUMERIC) * CAST(od.quantity AS NUMERIC)) AS preco_total_bruto
    FROM
        orders AS o
    LEFT JOIN
        order_details AS od
    ON
        o.order_id = od.order_id
) AS subquery
WHERE
    preco_total_bruto > 2000
ORDER BY preco_total_bruto asc;
```

## Conclusão

O desafio foi concluído de forma satisfatória, utilizando as ferramentas pedidas (Airflow, PostgreSQL e Meltano). Encontrei algumas dificuldades em relação à documentação fornecida pelos plugins do Meltano, que por vezes eram pouco esclarecedoras. No entanto, pesquisando em outras fontes, foi possível sanar os problemas. Quanto ao Airflow, já tinha familiaridade com essa ferramenta, o que facilitou a orquestração das tarefas. Em relação ao PostgreSQL, já possuía um vasto conhecimento, o que contribuiu para o sucesso do projeto. Uma observação é que o desafio foi desenvolvido em um ambiente da WSL, e talvez no Windows alguns comandos podem não funcionar.