#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_platform_detection() {
        let detector = SystemDetector::new();
        let platform = detector.platform();
        assert!(
            platform == "macos" || platform == "linux" || platform == "windows",
            "Unsupported platform: {}", platform
        );
    }

    #[test]
    fn test_arch_detection() {
        let detector = SystemDetector::new();
        let arch = detector.arch();
        assert!(
            arch == "aarch64" || arch == "x86_64",
            "Unsupported architecture: {}", arch
        );
    }

    #[test]
    fn test_memory_detection() {
        let detector = SystemDetector::new();
        let total_memory_gb = detector.total_memory_gb();
        assert!(total_memory_gb >= 4.0, "Detected unusually low memory: {}GB", total_memory_gb);
    }

    #[test]
    fn test_worktree_detection() {
        let detector = SystemDetector::new();
        assert!(!detector.is_inside_worktree(), "Should not be in a worktree by default");
    }
}

use sysinfo::System;
use std::process::Command;

pub struct SystemDetector {
    sys: System,
}

impl SystemDetector {
    pub fn new() -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();
        Self { sys }
    }

    pub fn platform(&self) -> String {
        let name = System::name().unwrap_or_default().to_lowercase();
        if name.contains("darwin") || name.contains("macos") {
            "macos".to_string()
        } else {
            name
        }
    }

    pub fn arch(&self) -> String {
        let arch = System::cpu_arch().to_lowercase();
        if arch.contains("arm64") || arch.contains("aarch64") {
            "aarch64".to_string()
        } else if arch.contains("x86_64") || arch.contains("amd64") {
            "x86_64".to_string()
        } else {
            arch
        }
    }

    pub fn total_memory_gb(&self) -> f64 {
        self.sys.total_memory() as f64 / 1024.0 / 1024.0 / 1024.0
    }

    pub fn is_inside_worktree(&self) -> bool {
        Command::new("git")
            .arg("rev-parse")
            .arg("--is-inside-work-tree")
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim() == "true")
            .unwrap_or(false)
    }
}
