# [tutortime.ca](https://tutortime.ca/)

Tutortime is an online time-bank platform focused on learning. Each user plays two roles on the platform:

- **As a teacher** you help other students in a subject you understand. You are awarded credits for your time
- **As a student** you can use your credits to schedule meetups with a teacher. They will help you learn about a subject you are interested in

Tutortime is a platform where users can learn new skills at no monetary cost.

## Setup

### Configuring the database

Tutortime uses Postgresql to store data. For development purposes it is sufficient to run a postgresql database in docker and connect directly through localhost

```shell
cd postgresql

# Build the tutortime database, the db credentials are specified in the Dockerfile
docker build . -t tutortime-db:latest

# Create a docker container using the image we just created
docker run -p 5432:5432/tcp -d tutortime-db
```

Ensure that the information specified in the [Dockerfile](postgres/Dockerfile) matches the db stanza of the [config.yaml](config.yaml)

### Frontend

The frontend is built in [VueJS](https://vuejs.org/) and uses [Vite](https://vite.dev/) as the Javascript bundler. You can compile and hot-reload for development by running:

```shell
cd frontend

# Bundle the frontend files, rebundle whenever there are changes
npm run watch
```

### Backend

You will need Golang installed to run the application. If you haven't installed Go yet, you can download it from the official Go website or from your official package repository:

- https://go.dev/doc/install

After go has been installed you can:

```shell
# Install the required dependencies
go get .

# Run the webserver
go run .
```
