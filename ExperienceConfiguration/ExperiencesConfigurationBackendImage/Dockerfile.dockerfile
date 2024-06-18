# Build stage
FROM maven:3.8.4-openjdk-17 as build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

# Run stage
FROM openjdk:17-slim
COPY --from=build /home/app/target/*.jar /usr/local/lib/springboot-app.jar
ENTRYPOINT ["java","-jar","/usr/local/lib/springboot-app.jar"]
