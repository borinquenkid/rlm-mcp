#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ollama_binary_check() {
        let manager = OllamaManager::new();
        // This test might fail if ollama is not installed, which is fine for TDD
        let installed = manager.is_installed();
        println!("Ollama installed: {}", installed);
    }

    #[test]
    fn test_ollama_service_check() {
        let manager = OllamaManager::new();
        // Checks if port 11434 is responding
        let running = tokio::runtime::Runtime::new().unwrap().block_on(manager.is_running());
        println!("Ollama running: {}", running);
    }
}

use std::process::Command;
use tokio::net::TcpStream;

pub struct OllamaManager {
    port: u16,
}

impl OllamaManager {
    pub fn new() -> Self {
        Self { port: 11434 }
    }

    pub fn is_installed(&self) -> bool {
        Command::new("ollama")
            .arg("--version")
            .output()
            .is_ok()
    }

    pub async fn is_running(&self) -> bool {
        TcpStream::connect(format!("127.0.0.1:{}", self.port)).await.is_ok()
    }

    pub async fn ensure_ready(&self, model: &str) -> Result<(), String> {
        if !self.is_installed() {
            println!("Ollama not found. Attempting to install...");
            self.install().map_err(|e| format!("Installation failed: {}", e))?;
        }

        if !self.is_running().await {
            println!("Ollama server is not running. Starting it...");
            self.start().map_err(|e| format!("Failed to start Ollama: {}", e))?;
            
            // Wait for it to become ready
            let mut attempts = 0;
            while !self.is_running().await && attempts < 10 {
                tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
                attempts += 1;
            }
            
            if !self.is_running().await {
                return Err("Ollama server failed to start after 10 seconds.".to_string());
            }
        }

        // Pull model if needed
        self.pull_model(model).await
    }

    pub fn install(&self) -> Result<(), String> {
        #[cfg(target_os = "macos")]
        {
            // On Mac, we can try to install via brew if available, or just guide the user
            // For a truly frictionless experience, we could download the binary.
            // For now, let's try brew as a common dev tool.
            let status = Command::new("brew")
                .arg("install")
                .arg("ollama")
                .status();
            
            if status.is_ok() && status.unwrap().success() {
                Ok(())
            } else {
                Err("Please install Ollama manually from https://ollama.com".to_string())
            }
        }

        #[cfg(target_os = "linux")]
        {
            let status = Command::new("sh")
                .arg("-c")
                .arg("curl -fsSL https://ollama.com/install.sh | sh")
                .status();
            
            if status.is_ok() && status.unwrap().success() {
                Ok(())
            } else {
                Err("Linux installation failed. Please run 'curl -fsSL https://ollama.com/install.sh | sh' manually.".to_string())
            }
        }

        #[cfg(target_os = "windows")]
        {
            Err("Windows auto-install not yet implemented. Please download from https://ollama.com".to_string())
        }
    }

    pub fn start(&self) -> Result<(), String> {
        // Start 'ollama serve' in the background
        Command::new("ollama")
            .arg("serve")
            .spawn()
            .map(|_| ())
            .map_err(|e| format!("Failed to spawn ollama serve: {}", e))
    }

    async fn pull_model(&self, model: &str) -> Result<(), String> {
        println!("Ensuring model {} is available...", model);
        let status = Command::new("ollama")
            .arg("pull")
            .arg(model)
            .status()
            .map_err(|e| format!("Failed to run ollama pull: {}", e))?;

        if status.success() {
            Ok(())
        } else {
            Err(format!("Ollama pull failed for model {}", model))
        }
    }
}
