package com.bezkoder.spring.jpa.postgresql.utils;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;

public class WebUtils {

  public static byte[] downloadImage(String urlString) throws IOException {
    URL url = new URL(urlString);
    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
    connection.setRequestMethod("GET");
    int responseCode = connection.getResponseCode();
    if (responseCode == HttpURLConnection.HTTP_OK) {
      try (InputStream inputStream = connection.getInputStream()) {
        return inputStream.readAllBytes();
      }
    } else {
      throw new IOException("Erreur de téléchargement de l'image : " + responseCode);
    }
  }
}
