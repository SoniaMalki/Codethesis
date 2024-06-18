# Build stage
FROM node:20.11.0 as build

# Set the working directory
WORKDIR /home/node/app

# Expose the port the app runs on
EXPOSE 4200

# Give node user permissions to write to global npm directories
RUN mkdir -p /usr/local/lib/node_modules && \
    chown -R node:node /usr/local/lib/node_modules && \
    mkdir -p /usr/local/bin && \
    chown -R node:node /usr/local/bin

# Change ownership of the app directory to user
RUN chown -R node:node /home/node/app

# Ensure the Angular cache directory exists and set ownership
RUN mkdir -p /home/node/app/.angular/cache && \
    chown -R node:node /home/node/app/.angular

# Switch to the new user
USER node

ENTRYPOINT ["/home/node/app/entrypoint.sh"]
