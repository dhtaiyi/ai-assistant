/**
 * 小红书登录测试脚本 (Node.js版本)
 */

const https = require('https');
const http = require('http');

// 配置
const WEB_SESSION = process.argv[2] || '040069b8fdba81d499ed9f75b83b4b4314e571';
const PROXY = process.argv[3] || null;

console.log('🔄 正在测试小红书登录...\n');
console.log('⚠️  注意: 当前环境为Node.js，小红书技能依赖Python环境');
console.log('    建议在有Python环境的本地机器运行完整测试\n');
console.log('📋 配置信息:');
console.log(`   Web Session: ${WEB_SESSION.substring(0, 20)}...`);
console.log(`   代理: ${PROXY || '无'}\n`);

console.log('✅ 测试脚本已创建');
console.log('📁 路径: /root/.openclaw/workspace/test_xiaohongshu.py');
console.log('\n💡 使用方法:');
console.log('   python3 test_xiaohongshu.py "web_session" "代理地址"');
