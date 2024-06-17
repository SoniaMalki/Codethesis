#!/bin/bash

# Correct ownership of all files - to be executed as root before switching to springuser
sudo chown -R springuser:springuser /home/springuser/app
sudo chown -R springuser:springuser /home/springuser/config_files

# Run Maven clean and package
mvn clean package -DskipTests -e -X

# Start the application
java -jar target/*.jar
