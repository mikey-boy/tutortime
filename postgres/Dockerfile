# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

# Set environment variables
ENV POSTGRES_DB=db
ENV POSTGRES_USER=tutortime
ENV POSTGRES_PASSWORD=tutortime

# Expose PostgreSQL default port
EXPOSE 5432

# Copy custom initialization scripts
# If you have any custom SQL scripts to initialize the database, place them in ./init.sql
# COPY init.sql /docker-entrypoint-initdb.d/

# Start PostgreSQL server
# CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
CMD ["postgres"]
