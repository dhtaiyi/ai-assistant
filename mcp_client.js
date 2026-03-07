#!/usr/bin/env node

const http = require('http');

const MCP_HOST = 'localhost';
const MCP_PORT = 18060;
const MCP_PATH = '/mcp';

let requestId = 1;
let sessionInitialized = false;

// Send MCP request and get response
function mcpRequest(requestData) {
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: MCP_HOST,
      port: MCP_PORT,
      path: MCP_PATH,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    
    req.on('error', reject);
    req.write(requestData);
    req.end();
  });
}

function createRequest(method, params = {}) {
  return JSON.stringify({
    jsonrpc: '2.0',
    id: String(requestId++),
    method,
    params
  });
}

async function main() {
  try {
    // Initialize
    console.log('Initializing MCP...');
    let response = await mcpRequest(createRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'cli', version: '1.0' }
    }));
    
    const initResult = JSON.parse(response);
    if (initResult.result) {
      console.log('✅ MCP Initialized');
      sessionInitialized = true;
    }
    
    // Now list tools
    response = await mcpRequest(createRequest('tools/list'));
    console.log('Tools response:', response.substring(0, 1000));
    
  } catch (e) {
    console.error('Error:', e.message);
  }
}

main();
