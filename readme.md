# Demo App

This is a demonstration application that includes FastAPI framework, MongoDB database connections, a MongoDB
database migration system, and an authorization system with Microsoft Azure Active Directory Identity.
It supports deploying with Docker.

---

## Prerequisites.

1. Implement a reverse proxy.
      1. Copy your certificate into ./reverse-proxy/certificates and name it as dtgo.com.crt.
      1. Copy your certificate's private key into ./reverse-proxy/certificates and name it as dtgo.com.key.
      1. Set up a reverse proxy.
         * Run `docker-compose -f ./reverse-proxy/docker-compose.yml up -d` command if you deploy with docker-compose
           command.
         * Run
           `docker stack deploy -c ./reverse-proxy/docker-compose.yml -c reverse-proxy/docker-stack.yml <stack name>`
           command if you deploy with docker stack command.

            For example:

            > docker stack deploy -c ./reverse-proxy/docker-compose.yml -c reverse-proxy/docker-stack.yml reverse-proxy

1. Create a local registry server if you deploy with docker stack command.

      Run `docker stack deploy -c ./docker-registry/docker-stack.yml <stack name>` command.

      For example:

      > docker stack deploy -c ./docker-registry/docker-stack.yml local-registry

1. Set up the MongoDB credentials.

      This application will create a root role user and an application user in a fresh installation.

      * Fill your root username in ./mongodb-credentials/root-username.txt.
      * Fill your root password in ./mongodb-credentials/root-password.txt.
      * Fill your application username in ./mongodb-credentials/application-username.txt.
      * Fill your application password in ./mongodb-credentials/application-password.txt.

1. Set up the Microsoft Azure Active Directory's protected web services application.
   
      After this, Azure AD will be stood for Microsoft Azure Active Directory.

      * Replace AZURE_AD_AUTHORITY environment in the docker-compose.yml file's app service with your Azure AD authority.
      * Replace AZURE_AD_AUDIENCE environment in the docker-compose.yml file's app service with your Azure AD audience
        which is your protected web service application ID.
      * Fill your Azure AD audience secret in ./azure_audience_secret.txt.

1. Set up the DNS name following the HOST environment's value in /.env.

      You can set your local DNS in development environment.

      For Windows example, append `127.0.0.1 web-services.dtgo.com` to C:\Windows\System32\drivers\etc\hosts.

**Note:** For production environment, you should grant permission of all credential files to users whom can run docker
and docker-compose commands only.

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

### For development environment:

#### To install/update this application.

Run the following command steps by steps.

1. `docker-compose build`
1. `docker-compose push`
1. `docker-compose -f docker-compose.yml -f docker-stack.yml -f docker-stack.development.yml config 
   | docker stack deploy -c - <stack name>`

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
1. `docker-compose -f docker-compose.yml -f docker-stack.yml config | docker stack deploy -c - <stack name>`

    For example:

    > docker-compose -f docker-compose.yml -f docker-stack.yml config | docker stack deploy -c - demo

#### To uninstall this application.

Run `docker stack rm <stack name>` command.

For example:
> docker stack rm demo

---

## How to roll back this application.

1. Run the following command below in your Windows PowerShell or your Linux terminal to roll back your database first.

      `docker exec $(docker ps --filter "name=<stack name>_app" --filter "status=running" -q -l)
   python /app/mongodb-migrations.py --action rollback`

      For example:

      > docker exec $(docker ps --filter "name=demo_app" --filter "status=running" -q -l)
   python /app/mongodb-migrations.py --action rollback

1. Check out to your previous version.
1. Update your application again.

---

## For developers:

### To test CSS/SCSS files without rebuilding the app service's image.
1. Check whether you have [NodeJS](https://nodejs.org/en) in your computer.
   If you do not have it, please install it first.
1. Mount **./app/assets:/app/assets** volume into the docker-compose.override.yml/docker-stack.development.yml file's
   app service depends on you deploy with docker-compose or docker stack command.
1. Run `docker-compose up -d` or `docker-compose -f docker-compose.yml -f docker-stack.yml 
   -f docker-stack.development.yml config | docker stack deploy -c - <stack name>` command.
1. Run `npm install` command to install all JavaScript libraries.
1. Run `npx mix watch` command to automatically recompile the files and rebuild your bundle.

### Helpful commands:
There are some helpful commands for all of you.

All commands have --help option to see how to use that command.

#### Create a MongoDB migration script file.
Run `docker exec $(docker ps --filter "name=<stack name>_app" --filter "status=running" -q -l)
python /app/mongodb-migration-creation-command/create_migration_script.py <filename>` command in your Windows PowerShell
or your Linux terminal. The system will create a migration script file with a current date and time prefix.
The created migration script file will have a ready code for writing a migration script.

For example:

> docker exec $(docker ps --filter "name=demo_app" --filter "status=running" -q -l)
python /app/mongodb-migration-creation-command/create_migration_script.py create_contact_collection
