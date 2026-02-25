#!/bin/bash

CORP_ID="wwf684d252386fc0b6"
AGENT_ID="1000002"
CORP_SECRET="aEgqy4MfNSXBWUoy9jgwZLiBfVTnd7POgRJzVUHq_Q0"

echo "╔════════════════════════════════════╗"
echo "║   🔍 企业微信API综合测试     ║"
echo "╚════════════════════════════════════╝"
echo ""

# 1. 获取Token
echo "1. 获取Access Token..."
TOKEN=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$CORP_ID&corpsecret=$CORP_SECRET" | jq -r '.access_token')
if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Token获取失败"
    exit 1
fi
echo "✅ Token: ${TOKEN:0:20}..."
echo ""

# 2. 测试各种API
echo "2. 测试API接口..."
echo ""

echo "   a) 发送消息..."
MSG=$(curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"touser":"@all","msgtype":"text","agentid":'"$AGENT_ID"',"text":{"content":"测试"}}' | jq -r '.errcode')
if [ "$MSG" = "0" ]; then
    echo "   ✅ 发送消息 - 正常"
else
    echo "   ❌ 发送消息 - 错误码: $MSG"
fi

echo ""
echo "   b) 获取部门列表..."
DEPT=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=$TOKEN" | jq -r '.errcode')
if [ "$DEPT" = "0" ]; then
    echo "   ✅ 获取部门 - 正常"
else
    echo "   ❌ 获取部门 - 错误码: $DEPT"
fi

echo ""
echo "   c) 获取用户列表..."
USERS=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=$TOKEN&department_id=1&fetch_child=0" | jq -r '.errcode')
if [ "$USERS" = "0" ]; then
    echo "   ✅ 用户列表 - 正常"
else
    echo "   ❌ 用户列表 - 错误码: $USERS"
fi

echo ""
echo "   d) 获取客户群列表..."
CUSTOM=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/list?access_token=$TOKEN" | jq -r '.errcode')
if [ "$CUSTOM" = "0" ]; then
    echo "   ✅ 客户列表 - 正常"
else
    echo "   ❌ 客户列表 - 错误码: $CUSTOM"
fi

echo ""
echo "3. 总结:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "如果以上都返回0，说明API权限正常"
echo ""
echo "401错误可能来自:"
echo "1. 特定的高级API(客户群发等)"
echo "2. 回调验证失败"
echo "3. 扩展内部错误"
echo ""
echo "建议检查:"
echo "- 企业微信应用的API权限列表"
echo "- IP白名单设置"
echo "- 扩展版本(2026.2.5)"
