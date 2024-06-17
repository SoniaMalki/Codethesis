FROM openjdk:17-slim

# Install Maven
RUN apt-get update && \
    apt-get install -y maven

# Arguments to pass UID and GID
ARG UID=1000
ARG GID=1000



# Creating a user and group with specified UID/GID
RUN groupadd -g ${GID} springuser && \
    useradd -u ${UID} -g springuser -m springuser

# Install sudo and add springuser to sudoers
RUN apt-get install -y sudo && \
    echo "springuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers


# Set the working directory
WORKDIR /home/springuser/app

# Switch to the new user after setting file permissions
USER springuser

ENTRYPOINT ["/home/springuser/app/entrypoint.sh"]
