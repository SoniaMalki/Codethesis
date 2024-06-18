FROM openjdk:17-slim

# Install Maven
RUN apt-get update && \
    apt-get install -y maven

# Arguments to pass UID and GID
ARG UID=1000
ARG GID=1000

# Creating a user and group with specified UID/GID
RUN if ! getent group ${GID}; then groupadd -g ${GID} user; fi && \
    if ! id -u ${UID}; then useradd -u ${UID} -g ${GID} -m user; fi

# Install sudo and add user to sudoers
RUN apt-get install -y sudo && \
    echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Set the working directory
WORKDIR /home/user/app

# Switch to the new user after setting file permissions
USER user

ENTRYPOINT ["/home/user/app/entrypoint.sh"]
