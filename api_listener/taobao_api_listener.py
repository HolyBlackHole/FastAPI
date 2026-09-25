#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝首页商品推荐接口监听脚本
==================================================
目标接口: https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0//
目标数据: mtopjsonppcrecommend24(...) 响应中的 data.data.list 商品列表
实现方式: 使用 Playwright 真实打开淘宝首页，通过CDP监听网络响应

使用方法:
1. 安装依赖: pip install playwright
2. 安装浏览器: python -m playwright install chromium
3. 运行脚本: python taobao_api_listener.py
4. 结果保存: 自动生成 taobao_goods_list.json
==================================================
"""

import json
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


# ============ JSONP解析模块 ============

def parse_jsonp(jsonp_str: str):
    """
    解析淘宝MTOP接口的JSONP响应。
    典型格式: mtopjsonppcrecommend24({api: "...", data: {...}, ret: [...]})
    注意: 响应中的JS对象键名通常没有双引号，需要转换为标准JSON后再解析。
    """
    if not jsonp_str:
        return None

    text = jsonp_str.strip()
    # 淘宝JSONP经常以 /**/ 开头做防护
    text = re.sub(r'^/\*.*?\*/', '', text).strip()

    # 匹配 callback({...}) 结构
    match = re.match(r'^[a-zA-Z0-9_]+\((.*)\);?\s*$', text, re.DOTALL)
    if not match:
        # 非JSONP，尝试直接作为JSON解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"[!] 无法识别的响应格式，前200字符: {text[:200]}")
            return None

    js_obj = match.group(1)

    # 给未加双引号的键名补上双引号: {key:  -> {"key":
    js_obj = re.sub(
        r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:',
        lambda m: f'{m.group(1)}"{m.group(2)}":',
        js_obj
    )

    # 修复尾逗号（如 {a:1, b:2,}）
    js_obj = re.sub(r',\s*([}\]])', r'\1', js_obj)

    try:
        return json.loads(js_obj)
    except json.JSONDecodeError as e:
        print(f"[!] JSON解析失败: {e}")
        print(f"[!] 出错位置附近: ...{js_obj[max(0, e.pos - 60):e.pos + 60]}...")
        return None


def extract_list(parsed: dict):
    """
    从解析后的响应中提取 data.data.list
    返回 (list_data, inner_meta) 二元组
    """
    if not parsed or not isinstance(parsed, dict):
        return None, None

    # 打印接口返回信息
    ret_info = parsed.get('ret', [])
    api_name = parsed.get('api', '')
    if ret_info:
        print(f"    接口: {api_name}")
        print(f"    返回: {ret_info[0] if isinstance(ret_info, list) else ret_info}")

    # 第一层 data
    data_wrap = parsed.get('data')
    if data_wrap is None:
        print("[!] 响应缺少 data 字段")
        return None, None

    # 淘宝偶尔把 data 序列化成字符串
    if isinstance(data_wrap, str):
        try:
            data_wrap = json.loads(data_wrap)
        except json.JSONDecodeError:
            print("[!] data 字段为字符串但无法二次解析为JSON")
            return None, None

    # 第二层 data  ——  目标 list 在这里
    inner = data_wrap.get('result', data_wrap)

    item_list = data_wrap.get('result') if isinstance(data_wrap, dict) else None

    # 兼容其他可能的列表字段名
    # if not item_list or not isinstance(item_list, list):
    #     for alt_key in ('items', 'resultList', 'cardList', 'feedList', 'goodsList'):
    #         if isinstance(data_wrap, dict) and isinstance(data_wrap.get(alt_key), list):
    #             item_list = data_wrap[alt_key]
    #             print(f"    [提示] 在 '{alt_key}' 字段中找到商品列表")
    #             break

    return item_list


# ============ 网络监听模块 ============
# https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/
def listen_and_capture(headless: bool = False, wait_seconds: int = 30, scroll_times: int = 3):
    """
    启动Playwright浏览器，打开淘宝首页，监听目标接口。

    参数:
        headless:     是否无头模式（默认False，可见浏览器方便观察；设为True则后台运行）
        wait_seconds: 最长等待秒数
        scroll_times: 向下滚动次数（触发更多推荐加载）
    返回:
        所有捕获到的list合并后的列表
    """
    target_api_keyword = 'mtop.relationrecommend.wirelessrecommend.recommend/2.0/'
    captured_lists = []
    capture_count = [0]  # 用列表包装以便在闭包中修改

    with sync_playwright() as p:
        print("[1/4] 启动 Chromium 浏览器...")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--start-maximized'
            ]
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            locale='zh-CN'
        )

        # 隐藏 webdriver 痕迹
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = { runtime: {} };
        """)

        page = context.new_page()

        # --- 注册响应监听 ---
        def on_response(response):
            url = response.url
            if target_api_keyword in url:
                print(f"url: {url}")
                try:
                    body = response.text()
                    status = response.status
                    print(f"\n[捕获] 状态码={status}  URL长度={len(url)}")

                    parsed = parse_jsonp(body)
                    print(f"parsed: {parsed}")
                    if parsed is None:
                        print("    [!] JSONP解析失败，跳过")
                        return

                    item_list = extract_list(parsed)
                    if item_list and isinstance(item_list, list) and len(item_list) > 0:
                        capture_count[0] += 1
                        captured_lists.extend(item_list)
                        print(f"    [✓] 第 {capture_count[0]} 次捕获到 {len(item_list)} 个商品")

                except Exception as e:
                    print(f"    [!] 处理响应时出错: {e}")

        page.on('response', on_response)

        # --- 打开淘宝首页 ---
        print("[2/4] 打开淘宝首页 https://www.taobao.com ...")
        page.goto('https://www.taobao.com/', wait_until='domcontentloaded', timeout=30000)

        print(f"[3/4] 监听网络中（共 {wait_seconds} 秒，滚动 {scroll_times} 次触发加载）...")
        start = time.time()

        # 等待并滚动触发更多推荐
        for i in range(scroll_times):
            elapsed = time.time() - start
            if elapsed >= wait_seconds:
                break
            # 等待一小段时间让请求发出
            time.sleep(3)
            page.evaluate("window.scrollBy({top: window.innerHeight, behavior: 'smooth'})")
            print(f"    已滚动 {i + 1}/{scroll_times} 次，已捕获 {capture_count[0]} 批数据...")

        # 剩余时间继续等待
        remaining = wait_seconds - (time.time() - start)
        if remaining > 0:
            print(f"    继续等待 {remaining:.0f} 秒...")
            time.sleep(remaining)

        print(f"[4/4] 监听结束，共捕获 {capture_count[0]} 次接口响应")
        browser.close()

    return captured_lists


# ============ 结果保存与展示 ============

def _save_results(all_items: list, batch_num: int, partial: bool = False):
    """将结果保存为JSON文件"""
    out_path = '/home/user/6139350345827965821/taobao_goods_list.json'
    data = {
        'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'target_api': 'mtop.relationrecommend.wirelessrecommend.recommend/2.0/',
        'capture_batches': batch_num,
        'total_items': len(all_items),
        'is_partial': partial,
        'list': all_items
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(items: list, max_show: int = 10):
    """打印商品摘要"""
    print("\n" + "=" * 70)
    print(f" 商品列表预览  ——  共 {len(items)} 个商品")
    print("=" * 70)
    for idx, item in enumerate(items[:max_show], 1):
        title = (
                item.get('title') or item.get('itemTitle') or item.get('name')
                or item.get('mainTitle') or item.get('itemName') or '(无标题)'
        )
        price = (
                item.get('price') or item.get('itemPrice')
                or (item.get('priceInfo') or {}).get('price')
                or item.get('reservePrice') or '-'
        )
        item_id = (
                item.get('itemId') or item.get('id') or item.get('auctionId') or '-'
        )
        pic = item.get('picUrl') or item.get('imgUrl') or item.get('pic') or item.get('image') or ''
        print(f"\n  [{idx}] ID: {item_id}")
        print(f"      标题: {str(title)[:60]}")
        print(f"      价格: {price}")
        if pic:
            print(f"      图片: {str(pic)[:90]}")
    if len(items) > max_show:
        print(f"\n  ... 另有 {len(items) - max_show} 个商品，详见 JSON 文件")
    print("=" * 70)


# ============ 主入口 ============

def main():
    print("=" * 70)
    print(" 淘宝商品推荐接口监听工具")
    print(f" 目标: mtop.relationrecommend.wirelessrecommend.recommend/2.0/ → data.data.list")
    print(f" 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # headless=False 可以看到真实浏览器窗口；如需后台运行改成 True
    items = listen_and_capture(headless=False, wait_seconds=30, scroll_times=3)

    if not items:
        print("\n[!] 没有捕获到任何商品数据。可能原因:")
        print("    1. 网络问题，淘宝页面未完全加载")
        print("    2. 接口路径发生变化")
        print("    3. 等待时间不够，可增大 wait_seconds 参数重试")
        return

    _save_results(items, capture_count=1, partial=False)  # type: ignore
    print_summary(items)

    out_path = '/home/user/6139350345827965821/taobao_goods_list.json'
    print(f"\n[✓] 完整数据已保存: {out_path}")


if __name__ == '__main__':
    data = listen_and_capture(headless=False, wait_seconds=30, scroll_times=3)
    print(data)
