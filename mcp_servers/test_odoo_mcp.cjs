#!/usr/bin/env node
/**
 * Test script for Odoo MCP Server
 * Tests the JSON-RPC connection and basic operations
 */

const http = require('http');

const ODOO_CONFIG = {
    host: 'localhost',
    port: 8069,
    database: 'ai_employee',
    username: 'admin',
    password: 'admin123'
};

let sessionId = null;

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
                        reject(new Error(json.error.data?.message || json.error.message));
                    } else {
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
                    reject(new Error(`Invalid JSON: ${body.substring(0, 100)}`));
                }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

async function runTests() {
    console.log('='.repeat(60));
    console.log('ODOO MCP SERVER TEST');
    console.log('='.repeat(60));
    console.log('');

    // Test 1: Authentication
    console.log('Test 1: Authentication');
    console.log('-'.repeat(40));
    try {
        const auth = await jsonRpc('/web/session/authenticate', {
            db: ODOO_CONFIG.database,
            login: ODOO_CONFIG.username,
            password: ODOO_CONFIG.password
        });
        console.log(`✓ Authenticated as: ${auth.username} (uid: ${auth.uid})`);
        console.log(`✓ Server version: ${auth.server_version}`);
        console.log(`✓ Database: ${auth.db}`);
    } catch (e) {
        console.log(`✗ Authentication failed: ${e.message}`);
        process.exit(1);
    }
    console.log('');

    // Test 2: List partners
    console.log('Test 2: List Partners');
    console.log('-'.repeat(40));
    try {
        const partners = await jsonRpc('/web/dataset/call_kw', {
            model: 'res.partner',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: [],
                fields: ['name', 'email'],
                limit: 5
            }
        });
        console.log(`✓ Found ${partners.length} partners`);
        partners.forEach(p => console.log(`  - ${p.name} (${p.email || 'no email'})`));
    } catch (e) {
        console.log(`✗ List partners failed: ${e.message}`);
    }
    console.log('');

    // Test 3: Create a test partner
    console.log('Test 3: Create Test Partner');
    console.log('-'.repeat(40));
    try {
        const partnerId = await jsonRpc('/web/dataset/call_kw', {
            model: 'res.partner',
            method: 'create',
            args: [{
                name: 'AI Employee Test Client',
                email: 'test@aiemployee.local',
                phone: '+1234567890'
            }],
            kwargs: {}
        });
        console.log(`✓ Created partner with ID: ${partnerId}`);
    } catch (e) {
        console.log(`✗ Create partner failed: ${e.message}`);
    }
    console.log('');

    // Test 4: Check accounting models
    console.log('Test 4: Check Accounting Models');
    console.log('-'.repeat(40));
    try {
        const invoices = await jsonRpc('/web/dataset/call_kw', {
            model: 'account.move',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: [['move_type', '=', 'out_invoice']],
                fields: ['name', 'state', 'amount_total'],
                limit: 5
            }
        });
        console.log(`✓ Invoice model accessible`);
        console.log(`✓ Found ${invoices.length} invoices`);
    } catch (e) {
        console.log(`! Note: ${e.message}`);
        console.log('  (This is expected if Accounting module is not installed)');
    }
    console.log('');

    console.log('='.repeat(60));
    console.log('ODOO CONNECTION TEST COMPLETE');
    console.log('='.repeat(60));
    console.log('');
    console.log('Odoo 19 is running and accessible via JSON-RPC API');
    console.log('MCP Server can connect to: http://localhost:8069');
    console.log('Database: ai_employee');
}

runTests().catch(console.error);
