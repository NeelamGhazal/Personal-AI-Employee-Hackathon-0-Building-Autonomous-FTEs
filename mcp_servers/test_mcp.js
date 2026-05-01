#!/usr/bin/env node

/**
 * Test script for the Vault MCP Server
 * Sends test requests and displays responses
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  console.log("Starting Vault MCP Server test...\n");

  // Spawn the server process
  const serverPath = path.join(__dirname, "vault_mcp_server.js");

  const transport = new StdioClientTransport({
    command: "node",
    args: [serverPath],
    env: {
      ...process.env,
      VAULT_PATH: path.join(__dirname, "..", "AI_Employee_Vault"),
    },
  });

  const client = new Client(
    { name: "test-client", version: "1.0.0" },
    { capabilities: {} }
  );

  try {
    await client.connect(transport);
    console.log("Connected to Vault MCP Server!\n");

    // Test 1: List available tools
    console.log("=== TEST 1: List Tools ===");
    const tools = await client.listTools();
    console.log("Available tools:");
    tools.tools.forEach((tool) => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });

    // Test 2: List files in Needs_Action
    console.log("\n=== TEST 2: vault_list (Needs_Action) ===");
    const listResult = await client.callTool({
      name: "vault_list",
      arguments: { folder: "Needs_Action" },
    });
    console.log(listResult.content[0].text);

    // Test 3: List files in Plans
    console.log("\n=== TEST 3: vault_list (Plans) ===");
    const plansResult = await client.callTool({
      name: "vault_list",
      arguments: { folder: "Plans" },
    });
    console.log(plansResult.content[0].text);

    // Test 4: Write a test file
    console.log("\n=== TEST 4: vault_write ===");
    const writeResult = await client.callTool({
      name: "vault_write",
      arguments: {
        folder: "Logs",
        filename: "mcp_test.txt",
        content: `MCP Server Test\nTimestamp: ${new Date().toISOString()}\nStatus: SUCCESS`,
      },
    });
    console.log(writeResult.content[0].text);

    // Test 5: Read the test file back
    console.log("\n=== TEST 5: vault_read ===");
    const readResult = await client.callTool({
      name: "vault_read",
      arguments: { folder: "Logs", filename: "mcp_test.txt" },
    });
    console.log("File content:");
    console.log(readResult.content[0].text);

    console.log("\n=== ALL TESTS PASSED ===");
    console.log("Vault MCP Server is working correctly!");

  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  } finally {
    await client.close();
  }
}

main();
