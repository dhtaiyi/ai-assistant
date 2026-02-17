import asyncio
import aiohttp
import json

FULL_COOKIE = "a1=19c38bfe575soyif192b9m5hpwx5ygtwre6wcv09w50000229354; abRequestId=e768898e-35ae-54a2-a4a1-587b896f9955; acw_tc=0a00d7db17709086539146891e5d9ec95dd302f396f9bfa5a90e01d76ec74b; gid=yjSqYDiiq2FJyjSqYDid2dh8W2Mlv3iyjJDjKjE62xUECE282vk9ES888JJjq2488KYy4jDd; id_token=VjEAALrTCyLKVl0M/MJxqa+vB6H0r2vVLUXY2L82iH32/oMAnYfYzR24Yr1IH/QXpWLNM0YKz95QbhLF2M0Vu7RzXKVyvMRtduzJNJG09QR+LPcPCdEfbPWIT7MqdkOO3WszqsFu; loadts=1770909161965; sec_poison_id=dfa5cfb3-8256-4129-9ef7-30e6d820db45; unread=%7B%22ub%22%3A%22696c890c000000000a03337b%22%2C%22ue%22%3A%22696eebf4000000002202f5d9%22%2C%22uc%22%3A33%7D; web_session=040069b8fdba81d499ed90a5b83b4ba5a54c4a; webBuild=5.11.0; webId=6b2463b432cb16239a3aeab9b3ab11df; websectiga=3fff3a6f9f07284b62c0f2ebf91a3b10193175c06e4f71492b60e056edcdebb2; xsecappid=xhs-pc-web"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.xiaohongshu.com",
    "referer": "https://www.xiaohongshu.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Cookie": FULL_COOKIE,
}

async def test():
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
    data = {"keyword": "穿搭", "page": 1, "page_size": 10}
    
    print("=== 不用代理测试 ===")
    
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(url, json=data) as resp:  # 不用代理
            print(f"  状态码: {resp.status}")
            result = await resp.json()
            print(f"  响应: {json.dumps(result, ensure_ascii=False)[:200]}")

asyncio.run(test())
