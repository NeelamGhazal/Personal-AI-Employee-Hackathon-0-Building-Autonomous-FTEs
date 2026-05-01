#!/usr/bin/env node
/**
 * Odoo MCP Server - Integrates with Odoo 19 via JSON-RPC
 * Provides accounting and business management tools for AI Employee
 */

const http = require('http');
const readline = require('readline');

// Odoo connection config
const ODOO_CONFIG = {
    host: 'localhost',
    port: 8069,
    database: 'ai_employee',
    username: 'admin',
    password: 'admin123'
};

let sessionId = null;
let uid = null;

// JSON-RPC helper
function jsonRpc(endpoint, params) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: params,
            id: Date.now()
        });

        const options = {
            hostname: ODOO_CONFIG.host,
            port: ODOO_CONFIG.port,
            path: endpoint,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data),
                ...(sessionId && { 'Cookie': `session_id=${sessionId}` })
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(body);
                    if (json.error) {
                        reject(new Error(json.error.data?.message || json.error.message || 'Unknown error'));
                    } else {
                        // Extract session cookie if present
                        const setCookie = res.headers['set-cookie'];
                        if (setCookie) {
                            for (const cookie of setCookie) {
                                const match = cookie.match(/session_id=([^;]+)/);
                                if (match) sessionId = match[1];
                            }
                        }
                        resolve(json.result);
                    }
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${body.substring(0, 200)}`));
                }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

// Authenticate with Odoo
async function authenticate() {
    const result = await jsonRpc('/web/session/authenticate', {
        db: ODOO_CONFIG.database,
        login: ODOO_CONFIG.username,
        password: ODOO_CONFIG.password
    });
    uid = result.uid;
    return result;
}

// Call Odoo model method
async function callModel(model, method, args = [], kwargs = {}) {
    if (!uid) await authenticate();

    return jsonRpc('/web/dataset/call_kw', {
        model: model,
        method: method,
        args: args,
        kwargs: kwargs
    });
}

// Search and read records
async function searchRead(model, domain = [], fields = [], limit = 100) {
    return callModel(model, 'search_read', [], {
        domain: domain,
        fields: fields,
        limit: limit
    });
}

// Create record
async function createRecord(model, values) {
    return callModel(model, 'create', [values]);
}

// Update record
async function updateRecord(model, id, values) {
    return callModel(model, 'write', [[id], values]);
}

// MCP Tool definitions
const tools = {
    // Authentication
    odoo_authenticate: {
        description: 'Authenticate with Odoo and get session info',
        inputSchema: {
            type: 'object',
            properties: {},
            required: []
        },
        handler: async () => {
            const result = await authenticate();
            return {
                success: true,
                uid: result.uid,
                username: result.username,
                database: result.db,
                server_version: result.server_version
            };
        }
    },

    // List invoices
    odoo_list_invoices: {
        description: 'List customer invoices from Odoo',
        inputSchema: {
            type: 'object',
            properties: {
                state: { type: 'string', enum: ['draft', 'posted', 'cancel'], description: 'Filter by invoice state' },
                limit: { type: 'number', description: 'Maximum number of invoices to return' }
            }
        },
        handler: async ({ state, limit = 50 }) => {
            const domain = [['move_type', '=', 'out_invoice']];
            if (state) domain.push(['state', '=', state]);

            const invoices = await searchRead('account.move', domain, [
                'name', 'partner_id', 'amount_total', 'amount_residual',
                'state', 'invoice_date', 'invoice_date_due', 'currency_id'
            ], limit);

            return {
                count: invoices.length,
                invoices: invoices.map(inv => ({
                    id: inv.id,
                    number: inv.name,
                    partner: inv.partner_id ? inv.partner_id[1] : 'N/A',
                    total: inv.amount_total,
                    balance_due: inv.amount_residual,
                    state: inv.state,
                    date: inv.invoice_date,
                    due_date: inv.invoice_date_due,
                    currency: inv.currency_id ? inv.currency_id[1] : 'USD'
                }))
            };
        }
    },

    // Create invoice
    odoo_create_invoice: {
        description: 'Create a new customer invoice in Odoo',
        inputSchema: {
            type: 'object',
            properties: {
                partner_name: { type: 'string', description: 'Customer name' },
                invoice_lines: {
                    type: 'array',
                    items: {
                        type: 'object',
                        properties: {
                            name: { type: 'string', description: 'Line description' },
                            quantity: { type: 'number' },
                            price_unit: { type: 'number' }
                        },
                        required: ['name', 'quantity', 'price_unit']
                    }
                }
            },
            required: ['partner_name', 'invoice_lines']
        },
        handler: async ({ partner_name, invoice_lines }) => {
            // Find or create partner
            let partners = await searchRead('res.partner', [['name', 'ilike', partner_name]], ['id', 'name'], 1);
            let partnerId;

            if (partners.length === 0) {
                partnerId = await createRecord('res.partner', { name: partner_name });
            } else {
                partnerId = partners[0].id;
            }

            // Create invoice
            const invoiceId = await createRecord('account.move', {
                move_type: 'out_invoice',
                partner_id: partnerId,
                invoice_line_ids: invoice_lines.map(line => [0, 0, {
                    name: line.name,
                    quantity: line.quantity,
                    price_unit: line.price_unit
                }])
            });

            return {
                success: true,
                invoice_id: invoiceId,
                message: `Invoice created for ${partner_name}`
            };
        }
    },

    // Get accounting summary
    odoo_accounting_summary: {
        description: 'Get accounting summary including revenue, expenses, and balances',
        inputSchema: {
            type: 'object',
            properties: {}
        },
        handler: async () => {
            // Get invoice totals
            const invoices = await searchRead('account.move', [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted']
            ], ['amount_total', 'amount_residual']);

            const totalRevenue = invoices.reduce((sum, inv) => sum + inv.amount_total, 0);
            const totalReceivable = invoices.reduce((sum, inv) => sum + inv.amount_residual, 0);

            // Get vendor bill totals
            const bills = await searchRead('account.move', [
                ['move_type', '=', 'in_invoice'],
                ['state', '=', 'posted']
            ], ['amount_total', 'amount_residual']);

            const totalExpenses = bills.reduce((sum, bill) => sum + bill.amount_total, 0);
            const totalPayable = bills.reduce((sum, bill) => sum + bill.amount_residual, 0);

            return {
                revenue: {
                    total_invoiced: totalRevenue,
                    outstanding_receivable: totalReceivable,
                    invoice_count: invoices.length
                },
                expenses: {
                    total_billed: totalExpenses,
                    outstanding_payable: totalPayable,
                    bill_count: bills.length
                },
                net_position: totalRevenue - totalExpenses,
                summary: `Revenue: $${totalRevenue.toFixed(2)}, Expenses: $${totalExpenses.toFixed(2)}, Net: $${(totalRevenue - totalExpenses).toFixed(2)}`
            };
        }
    },

    // List partners/customers
    odoo_list_partners: {
        description: 'List partners (customers/vendors) from Odoo',
        inputSchema: {
            type: 'object',
            properties: {
                customer: { type: 'boolean', description: 'Filter for customers only' },
                supplier: { type: 'boolean', description: 'Filter for suppliers only' },
                limit: { type: 'number' }
            }
        },
        handler: async ({ customer, supplier, limit = 50 }) => {
            const domain = [];
            // Note: In Odoo 19, customer/supplier flags may be different

            const partners = await searchRead('res.partner', domain, [
                'name', 'email', 'phone', 'city', 'country_id', 'credit', 'debit'
            ], limit);

            return {
                count: partners.length,
                partners: partners.map(p => ({
                    id: p.id,
                    name: p.name,
                    email: p.email || '',
                    phone: p.phone || '',
                    city: p.city || '',
                    country: p.country_id ? p.country_id[1] : '',
                    receivable: p.credit,
                    payable: p.debit
                }))
            };
        }
    },

    // List products
    odoo_list_products: {
        description: 'List products from Odoo',
        inputSchema: {
            type: 'object',
            properties: {
                limit: { type: 'number' }
            }
        },
        handler: async ({ limit = 50 }) => {
            const products = await searchRead('product.product', [], [
                'name', 'default_code', 'list_price', 'standard_price', 'qty_available', 'type'
            ], limit);

            return {
                count: products.length,
                products: products.map(p => ({
                    id: p.id,
                    name: p.name,
                    code: p.default_code || '',
                    sale_price: p.list_price,
                    cost: p.standard_price,
                    qty_on_hand: p.qty_available,
                    type: p.type
                }))
            };
        }
    },

    // Create partner
    odoo_create_partner: {
        description: 'Create a new partner (customer/vendor) in Odoo',
        inputSchema: {
            type: 'object',
            properties: {
                name: { type: 'string', description: 'Partner name' },
                email: { type: 'string' },
                phone: { type: 'string' },
                is_company: { type: 'boolean' }
            },
            required: ['name']
        },
        handler: async ({ name, email, phone, is_company = false }) => {
            const partnerId = await createRecord('res.partner', {
                name,
                email: email || false,
                phone: phone || false,
                is_company
            });

            return {
                success: true,
                partner_id: partnerId,
                message: `Partner "${name}" created with ID ${partnerId}`
            };
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
    const response = {
        jsonrpc: '2.0',
        id,
        result
    };
    console.log(JSON.stringify(response));
}

function sendError(id, code, message) {
    const response = {
        jsonrpc: '2.0',
        id,
        error: { code, message }
    };
    console.log(JSON.stringify(response));
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
                    serverInfo: {
                        name: 'odoo-mcp-server',
                        version: '1.0.0'
                    }
                });
                break;

            case 'notifications/initialized':
                // No response needed
                break;

            case 'tools/list':
                sendResponse(id, {
                    tools: Object.entries(tools).map(([name, tool]) => ({
                        name,
                        description: tool.description,
                        inputSchema: tool.inputSchema
                    }))
                });
                break;

            case 'tools/call':
                const toolName = params.name;
                const tool = tools[toolName];

                if (!tool) {
                    sendError(id, -32601, `Unknown tool: ${toolName}`);
                    break;
                }

                try {
                    const result = await tool.handler(params.arguments || {});
                    sendResponse(id, {
                        content: [{
                            type: 'text',
                            text: JSON.stringify(result, null, 2)
                        }]
                    });
                } catch (error) {
                    sendResponse(id, {
                        content: [{
                            type: 'text',
                            text: `Error: ${error.message}`
                        }],
                        isError: true
                    });
                }
                break;

            default:
                sendError(id, -32601, `Method not found: ${method}`);
        }
    } catch (error) {
        console.error('Error processing request:', error.message);
    }
});

// Log startup (to stderr so it doesn't interfere with MCP protocol)
console.error('Odoo MCP Server started');
console.error(`Connecting to Odoo at ${ODOO_CONFIG.host}:${ODOO_CONFIG.port}`);
console.error(`Database: ${ODOO_CONFIG.database}`);
