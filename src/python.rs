#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_uv_binary_check() {
        let manager = PythonManager::new();
        let installed = manager.is_uv_installed();
        println!("UV installed: {}", installed);
    }
}

use std::process::Command;

pub struct PythonManager {}

impl PythonManager {
    pub fn new() -> Self {
        Self {}
    }

    pub fn is_uv_installed(&self) -> bool {
        Command::new("uv")
            .arg("--version")
            .output()
            .is_ok()
    }

    pub fn ensure_ready(&self) -> Result<(), String> {
        if !self.is_uv_installed() {
            println!("uv not found. Attempting to install...");
            self.install_uv()?;
        }

        println!("Syncing Python environment...");
        self.sync_env()
    }

    fn install_uv(&self) -> Result<(), String> {
        #[cfg(not(target_os = "windows"))]
        {
            let status = Command::new("sh")
                .arg("-c")
                .arg("curl -LsSf https://astral.sh/uv/install.sh | sh")
                .status()
                .map_err(|e| format!("Failed to run uv installation script: {}", e))?;

            if status.success() {
                Ok(())
            } else {
                Err("uv installation failed.".to_string())
            }
        }

        #[cfg(target_os = "windows")]
        {
            let status = Command::new("powershell")
                .arg("-ExecutionPolicy")
                .arg("ByPass")
                .arg("-c")
                .arg("irm https://astral.sh/uv/install.ps1 | iex")
                .status()
                .map_err(|e| format!("Failed to run uv installation script: {}", e))?;

            if status.success() {
                Ok(())
            } else {
                Err("uv installation failed.".to_string())
            }
        }
    }

    fn sync_env(&self) -> Result<(), String> {
        // Run 'uv sync' to ensure .venv and dependencies are ready
        let status = Command::new("uv")
            .arg("sync")
            .status()
            .map_err(|e| format!("Failed to run uv sync: {}", e))?;

        if status.success() {
            Ok(())
        } else {
            Err("uv sync failed. Check your pyproject.toml.".to_string())
        }
    }
}
