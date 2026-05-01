#!/usr/bin/env node
/**
 * Install Accounting module in Odoo
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

async function installAccounting() {
    console.log('Installing Accounting module in Odoo...');
    console.log('');

    // Authenticate
    console.log('1. Authenticating...');
    const auth = await jsonRpc('/web/session/authenticate', {
        db: ODOO_CONFIG.database,
        login: ODOO_CONFIG.username,
        password: ODOO_CONFIG.password
    });
    console.log(`   ✓ Authenticated as ${auth.username}`);

    // Find accounting module
    console.log('2. Finding accounting module...');
    const modules = await jsonRpc('/web/dataset/call_kw', {
        model: 'ir.module.module',
        method: 'search_read',
        args: [],
        kwargs: {
            domain: [['name', '=', 'account']],
            fields: ['id', 'name', 'state', 'shortdesc']
        }
    });

    if (modules.length === 0) {
        console.log('   ✗ Accounting module not found');
        return;
    }

    const accountModule = modules[0];
    console.log(`   ✓ Found: ${accountModule.shortdesc} (state: ${accountModule.state})`);

    if (accountModule.state === 'installed') {
        console.log('   ℹ Accounting module already installed');
        return;
    }

    // Install the module
    console.log('3. Installing module (this may take a few minutes)...');
    try {
        await jsonRpc('/web/dataset/call_kw', {
            model: 'ir.module.module',
            method: 'button_immediate_install',
            args: [[accountModule.id]],
            kwargs: {}
        });
        console.log('   ✓ Module installed successfully');
    } catch (e) {
        console.log(`   ! Installation triggered: ${e.message}`);
        console.log('   (The module may still be installing in the background)');
    }

    console.log('');
    console.log('Done! Check Odoo at http://localhost:8069');
}

installAccounting().catch(console.error);
