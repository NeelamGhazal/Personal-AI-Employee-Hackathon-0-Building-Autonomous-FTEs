#!/usr/bin/env node
/**
 * Communications MCP Server - Handles Email and WhatsApp operations
 * Provides tools for AI Employee to manage communications
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const readline = require('readline');

// Paths
const PROJECT_ROOT = path.resolve(__dirname, '..');
const WATCHERS_PATH = path.join(PROJECT_ROOT, 'ai_employee_watchers', 'src', 'ai_employee_watchers');
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

// Helper to run Python scripts
function runPythonScript(scriptName, args = []) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(WATCHERS_PATH, scriptName);
        const proc = spawn('python', [scriptPath, ...args], {
            cwd: path.join(PROJECT_ROOT, 'ai_employee_watchers')
        });

        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data) => stdout += data);
        proc.stderr.on('data', (data) => stderr += data);

        proc.on('close', (code) => {
            resolve({ success: code === 0, output: stdout, error: stderr, code });
        });

        proc.on('error', (err) => reject(err));
    });
}

// Read messages from vault
function getMessages(type, domain = 'Personal', limit = 10) {
    const prefix = type.toUpperCase() + '_';
    const searchPath = path.join(VAULT_PATH, domain, 'Needs_Action');

    try {
        if (!fs.existsSync(searchPath)) return [];

        const files = fs.readdirSync(searchPath)
            .filter(f => f.startsWith(prefix) && f.endsWith('.md'))
            .sort()
            .reverse()
            .slice(0, limit);

        return files.map(f => {
            const content = fs.readFileSync(path.join(searchPath, f), 'utf-8');
            return { filename: f, content, path: path.join(searchPath, f) };
        });
    } catch (e) {
        return [];
    }
}

// MCP Tool definitions
const tools = {
    // Check Gmail
    comms_check_gmail: {
        description: 'Check for new Gmail messages (runs watcher once)',
        inputSchema: {
            type: 'object',
            properties: {
                once: { type: 'boolean', description: 'Run once and exit' }
            }
        },
        handler: async ({ once = true }) => {
            // Just return pending emails from vault since watcher needs OAuth
            const emails = getMessages('EMAIL', 'Personal', 10);
            return {
                source: 'gmail',
                pending_emails: emails.length,
                emails: emails.map(e => ({
                    filename: e.filename,
                    preview: e.content.substring(0, 200)
                }))
            };
        }
    },

    // Check WhatsApp
    comms_check_whatsapp: {
        description: 'Get pending WhatsApp messages from vault',
        inputSchema: {
            type: 'object',
            properties: {
                domain: { type: 'string', enum: ['Personal', 'Business'] }
            }
        },
        handler: async ({ domain = 'Personal' }) => {
            const messages = getMessages('WHATSAPP', domain, 10);
            return {
                source: 'whatsapp',
                domain: domain,
                pending_messages: messages.length,
                messages: messages.map(m => ({
                    filename: m.filename,
                    preview: m.content.substring(0, 200)
                }))
            };
        }
    },

    // Get all pending communications
    comms_get_pending: {
        description: 'Get all pending communications (email + WhatsApp) from both domains',
        inputSchema: {
            type: 'object',
            properties: {}
        },
        handler: async () => {
            const personalEmails = getMessages('EMAIL', 'Personal', 20);
            const personalWhatsapp = getMessages('WHATSAPP', 'Personal', 20);
            const businessEmails = getMessages('EMAIL', 'Business', 20);
            const businessWhatsapp = getMessages('WHATSAPP', 'Business', 20);

            return {
                personal: {
                    emails: personalEmails.length,
                    whatsapp: personalWhatsapp.length
                },
                business: {
                    emails: businessEmails.length,
                    whatsapp: businessWhatsapp.length
                },
                total: personalEmails.length + personalWhatsapp.length +
                       businessEmails.length + businessWhatsapp.length
            };
        }
    },

    // Create draft reply
    comms_create_draft: {
        description: 'Create a draft reply in the Drafts folder',
        inputSchema: {
            type: 'object',
            properties: {
                type: { type: 'string', enum: ['email', 'whatsapp'] },
                to: { type: 'string', description: 'Recipient' },
                subject: { type: 'string', description: 'Subject (for email)' },
                body: { type: 'string', description: 'Message body' }
            },
            required: ['type', 'to', 'body']
        },
        handler: async ({ type, to, subject, body }) => {
            const draftsPath = path.join(VAULT_PATH, 'Drafts');
            if (!fs.existsSync(draftsPath)) {
                fs.mkdirSync(draftsPath, { recursive: true });
            }

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
            const filename = `DRAFT_${type.toUpperCase()}_${timestamp}.md`;
            const filepath = path.join(draftsPath, filename);

            const content = `---
type: draft_${type}
to: ${to}
${type === 'email' ? `subject: ${subject || 'No Subject'}` : ''}
created_at: ${new Date().toISOString()}
status: draft
---

# Draft ${type === 'email' ? 'Email' : 'WhatsApp Message'}

## To
${to}

${type === 'email' ? `## Subject\n${subject || 'No Subject'}\n` : ''}
## Message
${body}

---
*Draft created by AI Employee*
`;
            fs.writeFileSync(filepath, content);

            return {
                success: true,
                filename: filename,
                path: filepath,
                message: `Draft created: ${filename}`
            };
        }
    },

    // Generate communications summary
    comms_generate_summary: {
        description: 'Generate a summary of all communications',
        inputSchema: {
            type: 'object',
            properties: {}
        },
        handler: async () => {
            const summary = {
                personal: {
                    pending_emails: getMessages('EMAIL', 'Personal', 100).length,
                    pending_whatsapp: getMessages('WHATSAPP', 'Personal', 100).length
                },
                business: {
                    pending_emails: getMessages('EMAIL', 'Business', 100).length,
                    pending_whatsapp: getMessages('WHATSAPP', 'Business', 100).length
                },
                generated_at: new Date().toISOString()
            };

            summary.total_pending =
                summary.personal.pending_emails + summary.personal.pending_whatsapp +
                summary.business.pending_emails + summary.business.pending_whatsapp;

            return summary;
        }
    }
};

// MCP Protocol Handler
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

function sendResponse(id, result) {
    console.log(JSON.stringify({ jsonrpc: '2.0', id, result }));
}

function sendError(id, code, message) {
    console.log(JSON.stringify({ jsonrpc: '2.0', id, error: { code, message } }));
}

rl.on('line', async (line) => {
    try {
        const request = JSON.parse(line);
        const { id, method, params } = request;

        switch (method) {
            case 'initialize':
                sendResponse(id, {
                    protocolVersion: '2024-11-05',
                    capabilities: { tools: {} },
                    serverInfo: { name: 'comms-mcp-server', version: '1.0.0' }
                });
                break;

            case 'notifications/initialized':
                break;

            case 'tools/list':
                sendResponse(id, {
                    tools: Object.entries(tools).map(([name, tool]) => ({
                        name, description: tool.description, inputSchema: tool.inputSchema
                    }))
                });
                break;

            case 'tools/call':
                const tool = tools[params.name];
                if (!tool) {
                    sendError(id, -32601, `Unknown tool: ${params.name}`);
                    break;
                }

                try {
                    const result = await tool.handler(params.arguments || {});
                    sendResponse(id, {
                        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
                    });
                } catch (error) {
                    sendResponse(id, {
                        content: [{ type: 'text', text: `Error: ${error.message}` }],
                        isError: true
                    });
                }
                break;

            default:
                sendError(id, -32601, `Method not found: ${method}`);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
});

console.error('Communications MCP Server started');
console.error('Tools: comms_check_gmail, comms_check_whatsapp, comms_get_pending, comms_create_draft');
