#!/usr/bin/env node
/**
 * Social Media MCP Server - Handles Facebook, Instagram, Twitter posting
 * Provides tools for AI Employee to manage social media presence
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
            if (code === 0) {
                resolve({ success: true, output: stdout, error: stderr });
            } else {
                resolve({ success: false, output: stdout, error: stderr, code });
            }
        });

        proc.on('error', (err) => {
            reject(err);
        });
    });
}

// Read recent posts from vault
function getRecentPosts(platform, limit = 10) {
    const socialMediaPath = path.join(VAULT_PATH, 'Business', 'Social_Media');
    const prefix = platform.toUpperCase() + '_POST_';

    try {
        const files = fs.readdirSync(socialMediaPath)
            .filter(f => f.startsWith(prefix) && f.endsWith('.md'))
            .sort()
            .reverse()
            .slice(0, limit);

        return files.map(f => {
            const content = fs.readFileSync(path.join(socialMediaPath, f), 'utf-8');
            return { filename: f, content };
        });
    } catch (e) {
        return [];
    }
}

// MCP Tool definitions
const tools = {
    // Post to Facebook
    social_post_facebook: {
        description: 'Create a post on Facebook (test mode creates action file without posting)',
        inputSchema: {
            type: 'object',
            properties: {
                message: { type: 'string', description: 'The message to post' },
                test_mode: { type: 'boolean', description: 'If true, only create action file without actual posting' }
            },
            required: ['message']
        },
        handler: async ({ message, test_mode = true }) => {
            const args = test_mode ? ['--test'] : ['--message', message];
            const result = await runPythonScript('facebook_poster.py', args);
            return {
                platform: 'facebook',
                message: message,
                test_mode: test_mode,
                success: result.success,
                output: result.output.substring(0, 500)
            };
        }
    },

    // Post to Instagram
    social_post_instagram: {
        description: 'Create a post on Instagram (test mode creates action file without posting)',
        inputSchema: {
            type: 'object',
            properties: {
                message: { type: 'string', description: 'The caption/message' },
                test_mode: { type: 'boolean', description: 'If true, only create action file' }
            },
            required: ['message']
        },
        handler: async ({ message, test_mode = true }) => {
            const args = test_mode ? ['--test'] : ['--message', message];
            const result = await runPythonScript('instagram_poster.py', args);
            return {
                platform: 'instagram',
                message: message,
                test_mode: test_mode,
                success: result.success,
                output: result.output.substring(0, 500)
            };
        }
    },

    // Post to Twitter
    social_post_twitter: {
        description: 'Create a tweet on Twitter/X (test mode creates action file without posting)',
        inputSchema: {
            type: 'object',
            properties: {
                message: { type: 'string', description: 'The tweet text (max 280 chars)' },
                test_mode: { type: 'boolean', description: 'If true, only create action file' }
            },
            required: ['message']
        },
        handler: async ({ message, test_mode = true }) => {
            if (message.length > 280) {
                return { error: 'Tweet exceeds 280 character limit', length: message.length };
            }
            const args = test_mode ? ['--test'] : ['--message', message];
            const result = await runPythonScript('twitter_poster.py', args);
            return {
                platform: 'twitter',
                message: message,
                character_count: message.length,
                test_mode: test_mode,
                success: result.success,
                output: result.output.substring(0, 500)
            };
        }
    },

    // Get recent posts
    social_get_recent_posts: {
        description: 'Get recent social media posts from the vault',
        inputSchema: {
            type: 'object',
            properties: {
                platform: { type: 'string', enum: ['facebook', 'instagram', 'twitter', 'all'] },
                limit: { type: 'number', description: 'Max number of posts to return' }
            }
        },
        handler: async ({ platform = 'all', limit = 5 }) => {
            const platforms = platform === 'all'
                ? ['facebook', 'instagram', 'twitter']
                : [platform];

            const results = {};
            for (const p of platforms) {
                results[p] = getRecentPosts(p, limit);
            }

            return {
                posts: results,
                total: Object.values(results).flat().length
            };
        }
    },

    // Generate social media summary
    social_generate_summary: {
        description: 'Generate a summary of social media activity',
        inputSchema: {
            type: 'object',
            properties: {}
        },
        handler: async () => {
            const summary = {
                facebook: getRecentPosts('facebook', 100).length,
                instagram: getRecentPosts('instagram', 100).length,
                twitter: getRecentPosts('twitter', 100).length,
                generated_at: new Date().toISOString()
            };

            summary.total = summary.facebook + summary.instagram + summary.twitter;

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
                    serverInfo: { name: 'social-media-mcp-server', version: '1.0.0' }
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

console.error('Social Media MCP Server started');
console.error('Tools: social_post_facebook, social_post_instagram, social_post_twitter');
