#!/bin/bash

# Correct ownership of all files - to be executed as root before switching to user
sudo chown -R user:user /home/user/app
sudo chown -R user:user /home/user/config_files

# Run Maven clean and package
mvn clean package -DskipTests 

# Start the application
java -jar target/*.jar
