# Demo App
This is a demonstration application that includes FastAPI framework, MongoDB database connections, 
and a MongoDB database migration system. It supports deploying with Docker.

---

## Prerequisites.
1. Setup MongoDB credentials.

    This application will create a root role user and an application user in a fresh installation.

    * Fill your root username in mongodb-credentials/root-username.txt
    * Fill your root password in mongodb-credentials/root-password.txt.
    * Fill your application username in mongodb-credentials/application-username.txt.
    * Fill your application password in mongodb-credentials/application-password.txt.
    
    For production environment, you should grant permission of those credential files to users whom can run docker
    and docker-compose commands only.

---

## To deploy with docker-compose command.
### For development environment:
#### To install/update this application.
Run `docker-compose up -d --build` command.
#### To uninstall this application.
Run `docker-compose down` command.

### For production environment:
#### To install/update this application.
Run `docker-compose -f docker-compose.yml up -d` command.
#### To uninstall this application.
Run `docker-compose -f docker-compose.yml down` command.

---

## To deploy with docker stack command.
_You have to run your Docker Engine in swarm mode._
### For development environment:
#### To install/update this application.
Run the following commands step by step.

1. `docker stack deploy --compose-file docker-registry.yml <stack name>` to create a local registry server.    

    For example:

    > docker stack deploy --compose-file docker-registry.yml registry

1. `docker-compose build`
1. `docker-compose push`
1. `docker-compose config | docker stack deploy -c - <stack name>`

    For example:

    > docker-compose config | docker stack deploy -c - demo

#### To uninstall this application.
Run `docker stack rm <stack name(s)>` command.

For example, if you would like to remove both of your application and your local registry server, just run the following
command below.
> docker stack rm demo registry

### For production environment:
#### To install/update this application.
Run the following commands step by step.

1. `docker stack deploy --compose-file docker-registry.yml <stack name>` to create a local registry server.    

    For example:

    > docker stack deploy --compose-file docker-registry.yml registry

1. `docker-compose -f docker-compose.yml build`
1. `docker-compose -f docker-compose.yml push`
1. `docker-compose -f docker-compose.yml config | docker stack deploy -c - <stack name>`

    For example:
    
    > docker-compose -f docker-compose.yml config | docker stack deploy -c - demo

#### To uninstall this application.
Run `docker stack rm <stack name(s)>` command.

For example, if you would like to remove both of your application and your local registry server, just run the following
command below.
> docker stack rm demo registry

---

## How to roll back this application.
1.  Run the following command below in your Windows PowerShell or your Linux terminal to roll back your database first.

    `docker exec $(docker ps --filter "name=<stack name>_app" --filter "status=running" -q -l)
    python /app/mongodb-migrations.py --action rollback`

    For example:

    > docker exec $(docker ps --filter "name=demo_app" --filter "status=running" -q -l)
    python /app/mongodb-migrations.py --action rollback

1.  Check out to your previous version.
1.  Update your application again.

---

## How to see MongoDB database migrations usage.
`docker exec $(docker ps --filter "name=<stack name>_app" --filter "status=running" -q -l)
python /app/mongodb-migrations.py --help`

For example:

> docker exec $(docker ps --filter "name=demo_app" --filter "status=running" -q -l) python /app/mongodb-migrations.py --help
