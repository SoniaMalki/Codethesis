package com.bezkoder.spring.jpa.postgresql.model.llmdata;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import jakarta.persistence.Lob;
import lombok.Data;

@Embeddable
public class ImageData {
  @Lob
  @Column(name = "picture_data", columnDefinition = "BYTEA")
  private byte[] data;

  // Constructors, getters, and setters
  public ImageData() {
  }

  public ImageData(byte[] data) {
    this.data = data;
  }

  public byte[] getData() {
    return data;
  }

  public void setData(byte[] data) {
    this.data = data;
  }
}
