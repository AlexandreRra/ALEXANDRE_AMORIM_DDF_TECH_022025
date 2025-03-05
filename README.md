# Project Setup and Execution Guide
[English Version](README.md) | [Versão em Português](README.pt-br.md)

This guide will help you set up and run the application using Docker Compose.

## Prerequisites

Make sure you have the following installed on your system:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/AlexandreRra/ALEXANDRE_AMORIM_DDF_TECH_022025
cd <your-project-directory>
```

### 2. Configure Environment Variables
Modify the `docker-compose.yml` file as needed, especially the environment variables for the API and database.

The structure of the environment variables in `docker-compose.yml` is as follows:

```
services
|
|---api
|    |
|    |---environment
|    |    |
|    |    |---KAGGLE_KEY
|    |    |---KAGGLE_USERNAME
```

Make sure to replace `KAGGLE_KEY` and `KAGGLE_USERNAME` with your Kaggle API credentials.

### 3. Build and Run the Containers
Run the following command in the project's root directory:
```sh
docker-compose up --build
```
This will build and start the following services:
- **PostgreSQL Database** (Port: `5432`)
- **Flask API** (Port: `5000`)
- **React Frontend** (Port: `3000`)

### 4. Access the Application
- **Frontend:** Open `http://localhost:3000` in your browser.
- **API:** Open `http://localhost:5000` in your browser or test with a tool like Postman.
- **Database:** Connect using `localhost:5432`, `myuser`, `mypassword`, and `mydatabase`.

## Stopping the Application
To stop the application and remove the containers, use:
```sh
docker-compose down
```

## Additional Commands
- To rebuild without using cache:
  ```sh
  docker-compose up --build --force-recreate
  ```
- To run in detached mode (background):
  ```sh
  docker-compose up -d
  ```
- To check logs:
  ```sh
  docker-compose logs -f
  ```

## Troubleshooting
- If you encounter permission issues with mounted volumes, try running:
  ```sh
  sudo chmod -R 777 backend frontend
  ```
- Ensure Docker is running before executing `docker-compose` commands.
- If port conflicts occur, change ports in `docker-compose.yml`.

## Notes
- **Database Persistence:** Data is stored in a Docker volume (`postgres_data`).
- **Hot Reloading:** Changes in the backend and frontend should reflect without restarting the containers.
- **Kaggle API Key:** Ensure your Kaggle API key is valid for required functionality.

Happy coding! 🚀

