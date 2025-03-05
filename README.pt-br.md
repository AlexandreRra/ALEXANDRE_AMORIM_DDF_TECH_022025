# Guia de Configuração e Execução do Projeto
[English Version](README.md) | [Versão em Português](README.pt-br.md)

Este guia ajudará você a configurar e executar a aplicação usando Docker Compose.

## Pré-requisitos

Certifique-se de ter os seguintes programas instalados no seu sistema:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Iniciando o Projeto

### 1. Clonar o Repositório
```sh
git clone https://github.com/AlexandreRra/ALEXANDRE_AMORIM_DDF_TECH_022025
cd <seu-diretório-do-projeto>
```

### 2. Configurar Variáveis de Ambiente
Modifique o arquivo `docker-compose.yml` para utilizar seu [token](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication) de acesso à API da kaggle para download do dataset. Altere os seguintes campos no `docker-compose.yml`:

```
services
|
|---api
|    |
|    |---environment
|    |    |
|    |    |---KAGGLE_KEY: <sua chave>
|    |    |---KAGGLE_USERNAME: <seu usuário>
```

Caso não queria utilizar a API do kaggle, é possível baixar diretamente o .zip do [dataset](https://www.kaggle.com/datasets/piyushjain16/amazon-product-data) e colocá-lo na pasta `./backend/data/raw`. Assim a aplicação pulará a parte do download e fará apenas a ingestão e limpeza dos dados

### 3. Construir e Executar os Containers
Execute o seguinte comando no diretório raiz do projeto:
```sh
docker-compose up --build
```
Isso construirá e iniciará os seguintes serviços:
- **Banco de Dados PostgreSQL** (Porta: `5432`)
- **API Flask** (Porta: `5000`)
- **Frontend React** (Porta: `3000`)

### 4. Acessar a Aplicação
- **Frontend:** Abra `http://localhost:3000` no seu navegador.
- **API:** Abra `http://localhost:5000` no navegador ou teste com uma ferramenta como Postman.
- **Swagger:** Abra `http://localhost:5000/apidocs` no navegador.
- **Banco de Dados:** Conecte-se usando `localhost:5432`, `myuser`, `mypassword` e `mydatabase`.

## Parando a Aplicação
Para parar a aplicação e remover os containers, use:
```sh
docker-compose down
```

## Comandos Adicionais
- Para reconstruir sem usar cache:
  ```sh
  docker-compose up --build --force-recreate
  ```
- Para rodar em modo desacoplado (em segundo plano):
  ```sh
  docker-compose up -d
  ```
- Para verificar os logs:
  ```sh
  docker-compose logs -f
  ```

## Solução de Problemas
- Certifique-se de que o Docker está em execução antes de executar os comandos `docker-compose`.
- Se houver conflitos de porta, altere as portas no `docker-compose.yml`.

## Notas
- **Persistência do Banco de Dados:** Os dados são armazenados em um volume do Docker (`postgres_data`).
- **Hot Reloading:** As alterações no backend e frontend devem ser refletidas sem a necessidade de reiniciar os containers.

