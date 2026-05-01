#!/usr/bin/env node

/**
 * Vault MCP Server - Provides file operations for the AI Employee Vault
 *
 * Tools:
 * - vault_read: Read a file from the vault
 * - vault_write: Write a file to the vault
 * - vault_list: List files in a vault folder
 * - vault_move: Move a file between folders (for approval workflow)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import * as fs from "fs";
import * as path from "path";

// Default vault path - can be overridden via environment variable
const VAULT_PATH = process.env.VAULT_PATH ||
  path.join(process.cwd(), "..", "AI_Employee_Vault");

// Allowed folders within the vault
const ALLOWED_FOLDERS = [
  "Inbox",
  "Needs_Action",
  "Plans",
  "Pending_Approval",
  "Approved",
  "Rejected",
  "Done",
  "Logs",
  "Accounting",
  "Briefings"
];

/**
 * Validate that a path is within the vault
 */
function validatePath(filePath) {
  const resolved = path.resolve(VAULT_PATH, filePath);
  if (!resolved.startsWith(path.resolve(VAULT_PATH))) {
    throw new Error("Path must be within the vault");
  }
  return resolved;
}

/**
 * Validate folder name
 */
function validateFolder(folder) {
  if (!ALLOWED_FOLDERS.includes(folder)) {
    throw new Error(`Invalid folder. Allowed: ${ALLOWED_FOLDERS.join(", ")}`);
  }
  return path.join(VAULT_PATH, folder);
}

// Create the MCP server
const server = new Server(
  {
    name: "vault-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "vault_read",
        description: "Read a file from the AI Employee Vault",
        inputSchema: {
          type: "object",
          properties: {
            folder: {
              type: "string",
              description: `Folder name: ${ALLOWED_FOLDERS.join(", ")}`,
            },
            filename: {
              type: "string",
              description: "Name of the file to read",
            },
          },
          required: ["folder", "filename"],
        },
      },
      {
        name: "vault_write",
        description: "Write a file to the AI Employee Vault",
        inputSchema: {
          type: "object",
          properties: {
            folder: {
              type: "string",
              description: `Folder name: ${ALLOWED_FOLDERS.join(", ")}`,
            },
            filename: {
              type: "string",
              description: "Name of the file to write",
            },
            content: {
              type: "string",
              description: "Content to write to the file",
            },
          },
          required: ["folder", "filename", "content"],
        },
      },
      {
        name: "vault_list",
        description: "List files in a vault folder",
        inputSchema: {
          type: "object",
          properties: {
            folder: {
              type: "string",
              description: `Folder name: ${ALLOWED_FOLDERS.join(", ")}`,
            },
          },
          required: ["folder"],
        },
      },
      {
        name: "vault_move",
        description: "Move a file between vault folders (for approval workflow)",
        inputSchema: {
          type: "object",
          properties: {
            source_folder: {
              type: "string",
              description: "Source folder",
            },
            dest_folder: {
              type: "string",
              description: "Destination folder",
            },
            filename: {
              type: "string",
              description: "File to move",
            },
          },
          required: ["source_folder", "dest_folder", "filename"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "vault_read": {
        const folderPath = validateFolder(args.folder);
        const filePath = path.join(folderPath, args.filename);

        if (!fs.existsSync(filePath)) {
          return {
            content: [{ type: "text", text: `Error: File not found: ${args.filename}` }],
            isError: true,
          };
        }

        const content = fs.readFileSync(filePath, "utf-8");
        return {
          content: [{ type: "text", text: content }],
        };
      }

      case "vault_write": {
        const folderPath = validateFolder(args.folder);
        const filePath = path.join(folderPath, args.filename);

        fs.writeFileSync(filePath, args.content, "utf-8");
        return {
          content: [{ type: "text", text: `Successfully wrote ${args.filename} to ${args.folder}` }],
        };
      }

      case "vault_list": {
        const folderPath = validateFolder(args.folder);

        if (!fs.existsSync(folderPath)) {
          return {
            content: [{ type: "text", text: `Folder is empty or does not exist: ${args.folder}` }],
          };
        }

        const files = fs.readdirSync(folderPath);
        const fileList = files.length > 0
          ? files.map(f => {
              const stat = fs.statSync(path.join(folderPath, f));
              return `${f} (${stat.size} bytes, ${stat.mtime.toISOString()})`;
            }).join("\n")
          : "No files in folder";

        return {
          content: [{ type: "text", text: `Files in ${args.folder}:\n${fileList}` }],
        };
      }

      case "vault_move": {
        const sourcePath = path.join(validateFolder(args.source_folder), args.filename);
        const destPath = path.join(validateFolder(args.dest_folder), args.filename);

        if (!fs.existsSync(sourcePath)) {
          return {
            content: [{ type: "text", text: `Error: Source file not found: ${args.filename}` }],
            isError: true,
          };
        }

        fs.renameSync(sourcePath, destPath);
        return {
          content: [{
            type: "text",
            text: `Moved ${args.filename} from ${args.source_folder} to ${args.dest_folder}`
          }],
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  console.error("Starting Vault MCP Server...");
  console.error(`Vault path: ${VAULT_PATH}`);

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("Vault MCP Server running on stdio");
}

main().catch(console.error);
