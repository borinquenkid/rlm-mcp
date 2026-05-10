mod system;
mod ollama;
mod python;

use crate::system::SystemDetector;
use crate::ollama::OllamaManager;
use crate::python::PythonManager;

use async_trait::async_trait;
use rust_mcp_schema::{
    CallToolRequestParams, CallToolResult, ListToolsResult, PaginatedRequestParams,
    RpcError, Implementation, InitializeResult, ProtocolVersion, ServerCapabilities,
    ServerCapabilitiesTools, Tool, TextContent, ContentBlock, ToolInputSchema,
};
use rust_mcp_sdk::{
    error::SdkResult,
    mcp_server::{server_runtime, McpServerOptions, ServerHandler, ServerRuntime},
    schema::schema_utils::CallToolError,
    McpServer, StdioTransport, ToMcpServerHandler, TransportOptions,
};
use serde_json::json;
use std::process::{Command, Stdio};
use std::io::Write;
use std::sync::Arc;

pub struct RlmHandler;

#[async_trait]
impl ServerHandler for RlmHandler {
    async fn handle_list_tools_request(
        &self,
        _params: Option<PaginatedRequestParams>,
        _runtime: Arc<dyn McpServer>,
    ) -> Result<ListToolsResult, RpcError> {
        let completion_schema: ToolInputSchema = serde_json::from_value(json!({
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt to process recursively."
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project identifier for persistent reasoning memory."
                },
                "model_name": {
                    "type": "string",
                    "description": "The name of the local model to use (default: deepseek-r1:7b).",
                    "default": "deepseek-r1:7b"
                },
                "environment": {
                    "type": "string",
                    "description": "The RLM execution environment (default: local).",
                    "default": "local"
                }
            },
            "required": ["prompt"]
        })).map_err(|e| RpcError::internal_error().with_message(format!("Failed to parse schema: {}", e)))?;

        let sync_schema: ToolInputSchema = serde_json::from_value(json!({
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the local repository root to synchronize."
                },
                "project_id": {
                    "type": "string",
                    "description": "Project identifier for this repository."
                }
            },
            "required": ["path", "project_id"]
        })).map_err(|e| RpcError::internal_error().with_message(format!("Failed to parse schema: {}", e)))?;

        Ok(ListToolsResult {
            meta: None,
            next_cursor: None,
            tools: vec![Tool {
                name: "rlm_completion".to_string(),
                description: Some("Perform a recursive language model completion using RLM with persistence.".to_string()),
                input_schema: completion_schema,
                annotations: None,
                execution: None,
                icons: vec![],
                meta: None,
                output_schema: None,
                title: Some("RLM Completion".to_string()),
            }, Tool {
                name: "sync_codebase".to_string(),
                description: Some("Incrementally synchronize RLM's understanding with local code changes.".to_string()),
                input_schema: sync_schema,
                annotations: None,
                execution: None,
                icons: vec![],
                meta: None,
                output_schema: None,
                title: Some("Sync Codebase".to_string()),
            }, Tool {
                name: "system_status".to_string(),
                description: Some("Check the current hardware and system status.".to_string()),
                input_schema: serde_json::from_value(json!({
                    "type": "object",
                    "properties": {}
                })).unwrap(),
                annotations: None,
                execution: None,
                icons: vec![],
                meta: None,
                output_schema: None,
                title: Some("System Status".to_string()),
            }],
        })
    }

    async fn handle_call_tool_request(
        &self,
        params: CallToolRequestParams,
        _runtime: Arc<dyn McpServer>,
    ) -> Result<CallToolResult, CallToolError> {
        if params.name == "system_status" {
            let detector = SystemDetector::new();
            let status_text = format!(
                "OS: {}\nArch: {}\nTotal Memory: {:.2} GB",
                detector.platform(),
                detector.arch(),
                detector.total_memory_gb()
            );
            return Ok(CallToolResult {
                content: vec![ContentBlock::TextContent(TextContent::new(status_text, None, None))],
                is_error: None,
                meta: None,
                structured_content: None,
            });
        }

        if params.name == "sync_codebase" {
            let args = params.arguments.unwrap_or_default();
            let path = args.get("path").and_then(|v| v.as_str()).ok_or_else(|| CallToolError::new(RpcError::invalid_params()))?;
            let project_id = args.get("project_id").and_then(|v| v.as_str()).ok_or_else(|| CallToolError::new(RpcError::invalid_params()))?;
            
            // 1. Calculate diffs (simple version: list files)
            // In a real production tool, we'd use the sha2 crate here to compare hashes.
            // For now, we'll prompt RLM to perform the scan.
            let sync_prompt = format!(
                "Scan the repository at {} and update your consolidated knowledge base for project '{}'. 
                Focus on identifying architectural changes and new classes.", 
                path, project_id
            );

            // 2. Call completion with the sync prompt
            return self.call_bridge(&sync_prompt, "deepseek-r1:7b", "local", Some(project_id)).await;
        }

        if params.name != "rlm_completion" {
            return Err(CallToolError::new(RpcError::method_not_found()));
        }

        let args = params.arguments.unwrap_or_default();
        let prompt = args.get("prompt").and_then(|v| v.as_str()).ok_or_else(|| CallToolError::new(RpcError::invalid_params()))?;
        let project_id = args.get("project_id").and_then(|v| v.as_str());
        let model_name = args.get("model_name").and_then(|v| v.as_str()).unwrap_or("deepseek-r1:7b");
        let environment = args.get("environment").and_then(|v| v.as_str()).unwrap_or("local");

        self.call_bridge(prompt, model_name, environment, project_id).await
    }
}

impl RlmHandler {
    async fn call_bridge(&self, prompt: &str, model_name: &str, environment: &str, project_id: Option<&str>) -> Result<CallToolResult, CallToolError> {
        // Call the Python bridge
        let mut child = Command::new("uv")
            .arg("run")
            .arg("python")
            .arg("rlm_bridge.py")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|e| CallToolError::new(RpcError::internal_error().with_message(format!("Failed to spawn bridge: {}", e))))?;

        let input = json!({
            "prompt": prompt,
            "model_name": model_name,
            "base_url": "http://localhost:11434/v1",
            "environment": environment,
            "project_id": project_id
        });

        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(input.to_string().as_bytes()).ok();
        }

        let output = child.wait_with_output()
            .map_err(|e| CallToolError::new(RpcError::internal_error().with_message(format!("Failed to read bridge output: {}", e))))?;

        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let result: serde_json::Value = serde_json::from_str(&stdout)
                .map_err(|e| CallToolError::new(RpcError::internal_error().with_message(format!("Failed to parse JSON: {}", e))))?;
            
            if result["status"] == "success" {
                let response_text = result["response"].as_str().unwrap().to_string();
                Ok(CallToolResult {
                    content: vec![ContentBlock::TextContent(TextContent::new(response_text, None, None))],
                    is_error: None,
                    meta: None,
                    structured_content: None,
                })
            } else {
                Err(CallToolError::new(RpcError::internal_error().with_message(format!("RLM Error: {}", result["message"]))))
            }
        } else {
            Err(CallToolError::new(RpcError::internal_error().with_message("RLM Bridge process failed")))
        }
    }
}

#[tokio::main]
async fn main() -> SdkResult<()> {
    println!("Initializing rlm-mcp...");

    // 1. Detect Hardware & OS
    let detector = SystemDetector::new();
    println!("Detected: {} on {}", detector.arch(), detector.platform());
    println!("Total Memory: {:.2} GB", detector.total_memory_gb());

    // 2. Automated Setup
    let ollama = OllamaManager::new();
    let python = PythonManager::new();

    if let Err(e) = ollama.ensure_ready("deepseek-r1:7b").await {
        eprintln!("Ollama setup failed: {}", e);
        return Ok(());
    }

    if let Err(e) = python.ensure_ready() {
        eprintln!("Python setup failed: {}", e);
        return Ok(());
    }

    println!("rlm-mcp is ready!");

    // 3. MCP Server Setup
    let server_details = InitializeResult {
        server_info: Implementation {
            name: "rlm-mcp".into(),
            version: "0.1.0".into(),
            title: Some("RLM MCP Server".into()),
            description: Some("Recursive Language Model MCP Server".into()),
            icons: vec![],
            website_url: None,
        },
        capabilities: ServerCapabilities {
            tools: Some(ServerCapabilitiesTools { list_changed: None }),
            ..Default::default()
        },
        meta: None,
        instructions: None,
        protocol_version: ProtocolVersion::V2025_11_25.into(),
    };

    let transport = StdioTransport::new(TransportOptions::default())?;
    let handler = RlmHandler {};

    let server: Arc<ServerRuntime> = server_runtime::create_server(McpServerOptions {
        server_details,
        transport,
        handler: handler.to_mcp_server_handler(),
        task_store: None,
        client_task_store: None,
        message_observer: None,
    });

    println!("Starting MCP server on stdio...");
    server.start().await.map_err(|e| {
        eprintln!("Server error: {}", e);
        e
    })?;

    Ok(())
}
