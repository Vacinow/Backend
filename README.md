# Backend

## 🏁 Rodando o projeto

Para rodar o projeto é necessário ter credenciais válidas pra a integração com a AWS e são necessárias algumas variáveis de ambiente. Dessa forma é definir as seguintes varávies de ambiente com os seguintes valores:

```ENV
AWS_ACCESS_KEY_ID=<O-ID-DA-SUA-CHAVE-AQUI>
AWS_SECRET_ACCESS_KEY=<A-SUA-CHAVE-AQUI>
AWS_DEFAULT_REGION=us-east-1
DB_ENGINE=postgresql
DB_USERNAME=grupodoze
DB_PASSWORD=<SENHA-DO-BD-AQUI>
DB_HOST=vacinow-db.cvwjx0keomx6.sa-east-1.rds.amazonaws.com
DB_PORT=5432
DB_DATABASE=vacinow-db
```

Pode-se colocar essas definições em um arquivo chamado `.env` e colocar o arquivo na raiz do projeto.

Então, para rodar a aplicação com esse arquivo, é necessário executar na raiz do projeto o seguinte comando:


```bash
docker-compose --env-file .env up --build
```

## 📝 Documentação

É possível ver a diagrama de classe do projeto a seguir:

![Diagrama de classe do projeto](./assets/diagrama_de_classes.png)