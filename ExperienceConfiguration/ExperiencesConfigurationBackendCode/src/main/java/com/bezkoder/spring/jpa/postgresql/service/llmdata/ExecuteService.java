package com.bezkoder.spring.jpa.postgresql.service.llmdata;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import org.springframework.stereotype.Service;

@Service
public class ExecuteService {

  private Process commandProcess; // Process reference

  private static final String BATCH_FILE_PATH = "K:\\Games\\task-configuration-backend\\backend\\Hub-Backend\\command_executor.bat";

  public void executePythonScript(String parameter) throws IOException {
    if (commandProcess == null || !isProcessRunning()) {
      System.out.println("Starting a new command window...");
      // Execute the batch script directly, monitoring its output and status
      commandProcess = Runtime.getRuntime().exec("cmd /c " + BATCH_FILE_PATH);
      waitForProcessInitialization();
    }

    // Construct the command and write to commands.txt
    String command = String.format("python ../Codethesis/main.py %s", parameter);
    try (BufferedWriter writer = new BufferedWriter(new FileWriter("./commands.txt"))) {
      writer.write(command);
    }
  }

  private boolean isProcessRunning() {
    if (commandProcess == null) return false;

    try {
      commandProcess.exitValue();
      return false; // Process has terminated
    } catch (IllegalThreadStateException ex) {
      return true; // Process is still running
    }
  }

  private void waitForProcessInitialization() {
    try {
      Thread.sleep(2000); // Wait a bit for the process to stabilize
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
    }
  }
}


