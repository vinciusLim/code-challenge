# Documentação do Desafio de Código Técnico da Indicium

## Configuração do Banco de Dados

### Banco de dados Northwind

Para configurar o banco de dados Northwind, execute o comando `docker compose up` para inicializar o arquivo northwind.sql e o Docker. Para visualizar e gerenciar o banco de dados, utilize o pgAdmin. O banco contém um total de 13 tabelas.

![Imagem do PostgreSQL](imagens/image.png)

## Iniciando o Projeto de carregador de dados com Meltano

Para começar um projeto Meltano, utilize o comando `meltano init meu_projeto`. O projeto inclui um processo ETL completo, que envolve extração de dados de dois fontes externas (um CSV e um banco PostgreSQL local) e carregamento desses dados em um banco interno denominado "banco_destino".

## Transferência de CSV Externo para CSV Local

O primeiro passo envolve a consolidação de arquivos CSV de detalhes de pedidos locais em um único arquivo CSV.

### Comando

```bash
meltano el tap-csv-tipo1 target-csv-tipo1
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

O segundo passo consiste na extração de dados de um banco de dados local e sua exportação para arquivos CSV em um diretório local.

### Comando

```bash
meltano el tap-postgres-tipo1 target-csv-tipo2
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

O último passo envolve a importação de arquivos CSV locais para o banco de dados "banco_destino".

### Comando

```bash
meltano el tap-csv-tipo2 target-postgres-tipo1
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

Utilizando Airflow, é possível agendar a execução dos jobs `tap_csv_to_target_csv_task` e `tap_postgres_to_target_csv_task`, responsáveis por carregar dados externos para o local. Após a conclusão desses jobs, o job `tap_csv_to_target_postgres_task` carrega esses dados locais para o banco de dados "banco_destino". O Airflow roda localmente, registrando as execuções e a qualidade dos processos, além de exibir um gráfico que mostra a ordem de execução dos jobs.

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

A documentação do Desafio de Código Técnico da Indicium oferece uma visão mais completa e compreensível do processo de ETL. As informações detalhadas, os exemplos e as ilustrações facilitam o uso do código e a execução do desafio, utlizando o carregador de dados Meltano e o agendador de fluxo Airflow.