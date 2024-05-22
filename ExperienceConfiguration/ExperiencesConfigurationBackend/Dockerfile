# Build stage
FROM maven:3.8.4-openjdk-17 as build
WORKDIR /home/app
COPY pom.xml .
COPY src ./src
# Skip tests while building the package
RUN mvn clean package -DskipTests

# Run stage
FROM openjdk:17-slim
WORKDIR /home/app
COPY --from=build /home/app/target/*.jar /usr/local/lib/springboot-app.jar
VOLUME /home/app
ENTRYPOINT ["java","-jar","/usr/local/lib/springboot-app.jar"]
