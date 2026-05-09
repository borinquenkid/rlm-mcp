#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_platform_detection() {
        let detector = SystemDetector::new();
        let platform = detector.platform();
        
        // Assert that we detect one of the supported platforms
        assert!(
            platform == "macos" || platform == "linux" || platform == "windows",
            "Unsupported platform: {}", platform
        );
    }

    #[test]
    fn test_arch_detection() {
        let detector = SystemDetector::new();
        let arch = detector.arch();
        
        // Assert that we detect one of the supported architectures
        assert!(
            arch == "aarch64" || arch == "x86_64",
            "Unsupported architecture: {}", arch
        );
    }

    #[test]
    fn test_memory_detection() {
        let detector = SystemDetector::new();
        let total_memory_gb = detector.total_memory_gb();
        
        // Most modern dev machines have at least 4GB
        assert!(total_memory_gb >= 4.0, "Detected unusually low memory: {}GB", total_memory_gb);
    }
}

use sysinfo::{System};

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
}
