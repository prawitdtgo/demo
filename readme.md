# Demo App
This is a demonstration application that includes FastAPI framework, MongoDB database connections, 
and a MongoDB database migration system. It supports deploying with Docker.

---

## Prerequisites.
1. Set up MongoDB credentials.

    This application will create a root role user and an application user in a fresh installation.

    * Fill your root username in ./mongodb-credentials/root-username.txt
    * Fill your root password in ./mongodb-credentials/root-password.txt.
    * Fill your application username in ./mongodb-credentials/application-username.txt.
    * Fill your application password in ./mongodb-credentials/application-password.txt.
    
    For production environment, you should grant permission of those credential files to users whom can run docker
    and docker-compose commands only.

1. Set up this application's certificate.
    1. Copy your certificate into ./certificates and name it as dtgo.com.crt.
    1. Copy your certificate's private key into ./certificates and name it as dtgo.com.key.
1. Set up your DNS name following HOST environment's value in /.env.

    You can set your local DNS in development environment.

    For Windows example, append `127.0.0.1 web-services.dtgo.com` to C:\Windows\System32\drivers\etc\hosts.

---

## To deploy with docker-compose command.
### For development environment:
#### To install/update this application.
Run `docker-compose up -d` command.

**Note:** To rebuild the images, use `docker-compose up -d --build` command.

#### To uninstall this application.
Run `docker-compose down` command.

### For production environment:
#### To install/update this application.
Run `docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d` command.
#### To uninstall this application.
Run `docker-compose down` command.

---

## To deploy with docker stack command.
_You have to run your Docker Engine in swarm mode._

### Prerequisites.
1. Create a local registry server.

    Run `docker stack deploy --compose-file docker-registry.yml <stack name>` command.

    For example:

    > docker stack deploy --compose-file docker-registry.yml local-registry

### For development environment:
#### To install/update this application.
Run the following command steps by steps.

1. `docker-compose build`
1. `docker-compose push`
1. `docker-compose -f docker-compose.yml -f docker-stack.yml -f docker-stack.development.yml config
    | docker stack deploy -c - <stack name>` command.

    For example:

    > docker-compose -f docker-compose.yml -f docker-stack.yml -f docker-stack.development.yml config
    | docker stack deploy -c - demo

#### To uninstall this application.
Run `docker stack rm <stack name>` command.

For example:
> docker stack rm demo

### For production environment:
#### To install/update this application.
Run the following command steps by steps.

1. `docker-compose build`
1. `docker-compose push`
1. `docker-compose -f docker-compose.yml -f docker-stack.yml config
    | docker stack deploy -c - <stack name>` command.

    For example:

    > docker-compose -f docker-compose.yml -f docker-stack.yml config | docker stack deploy -c - demo

#### To uninstall this application.
Run `docker stack rm <stack name>` command.

For example:
> docker stack rm demo

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
Run `docker exec $(docker ps --filter "name=<stack name>_app" --filter "status=running" -q -l)
python /app/mongodb-migrations.py --help` command in your Windows PowerShell or your Linux terminal.

For example:

> docker exec $(docker ps --filter "name=demo_app" --filter "status=running" -q -l) python /app/mongodb-migrations.py --help
