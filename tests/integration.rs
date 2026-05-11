use std::process::{Command, Stdio};
use std::io::{Write, BufRead, BufReader};
use std::time::Duration;
use tokio::time::timeout;

#[tokio::test]
async fn test_server_status_tool() {
    // Spawn the server as a subprocess
    let mut child = Command::new("cargo")
        .arg("run")
        .arg("--quiet")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("Failed to start rlm-mcp server");

    // Give it a moment to initialize
    tokio::time::sleep(Duration::from_secs(5)).await;

    // Send a JSON-RPC request for system_status
    let request = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "system_status",
            "arguments": {}
        },
        "id": 1
    });

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(request.to_string().as_bytes()).unwrap();
        stdin.write_all(b"\n").unwrap();
    }

    // Read the response
    let stdout = child.stdout.take().unwrap();
    let reader = BufReader::new(stdout);
    
    // Read the response using a blocking approach with a timeout wrapper, or simply read.
    // lines.next() is synchronous, so we wrap the whole reading block.
    let response_line = std::thread::spawn(move || {
        let mut lines = reader.lines();
        lines.next().unwrap().unwrap()
    })
    .join()
    .expect("Failed to read from child process");

    let response: serde_json::Value = serde_json::from_str(&response_line).unwrap();
    
    // Verify the response
    assert_eq!(response["id"], 1);
    assert!(response["result"]["content"][0]["text"].as_str().unwrap().contains("OS:"));
    
    // Cleanup
    child.kill().unwrap();
}
