import json
import hashlib
import requests
import re
import time
from datetime import datetime


headers = {
    "referer": "https://www.taobao.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
}

cookies = {
    "cna": "JgeHItTEvQ4BASQIgkDE9RDx",
    "thw": "xx",
    "tracknick": "allureloveover",
    "havana_lgc2_0": "eyJoaWQiOjI3NzY4MjUxMzIsInNnIjoiZDNiODgzNDA3NDllN2QwMGVlZmIzMDU0NGQ2YjVhOTciLCJzaXRlIjowLCJ0b2tlbiI6IjFMNnZyaUhDM1JVTmpvazIzU1V2djhnIn0",
    "_hvn_lgc_": "0",
    "wk_cookie2": "1ec12fa7919c74640c35e43e9917e620",
    "wk_unb": "UU8PbVS5rhnL%2Fg%3D%3D",
    "cookie2": "1f08df16c305d2f6d43129d4c950c8fb",
    "t": "6d7fa30926ef99ed8b6aa8b1c846aa61",
    "_tb_token_": "88f37a7e09a3",
    "xlly_s": "1",
    "unb": "2776825132",
    "uc1": "cookie21=VT5L2FSpccLuJBreK%2BBd&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&pas=0&existShop=false&cookie14=UoYXLP%2FtjV9uXQ%3D%3D&cookie15=VT5L2FSpMGV7TQ%3D%3D",
    "sn": "",
    "uc3": "nk2=An0AJ391v17oG7PGerI%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UU8PbVS5rhnL%2Fg%3D%3D&vt3=F8dD1fULHgVD2EB8FHg%3D",
    "csg": "af678cca",
    "lgc": "allureloveover",
    "cancelledSubSites": "empty",
    "cookie17": "UU8PbVS5rhnL%2Fg%3D%3D",
    "dnk": "cy77727",
    "skt": "11b800c899615528",
    "existShop": "MTc5MDIzMDQ4OQ%3D%3D",
    "uc4": "nk4=0%40AJY%2BJejEP3pd2o%2BcfpbtURAnqAUYPjvcmQ%3D%3D&id4=0%40U22IAPj0Hf2I%2Fzg19yeJKIjbuOWE",
    "_cc_": "WqG3DMC9EA%3D%3D",
    "_l_g_": "Ug%3D%3D",
    "sg": "r2d",
    "_nk_": "allureloveover",
    "cookie1": "VFO7NYJqjvNC8%2BG0NxaCwxWLrP8sYJPYT4ItNvZV4oY%3D",
    "sgcookie": "E100b87XfAybK4sl0YgKr60%2BYcVWqE3bKftfuiKBHqKlSfzyId6R37aSuu82VwWLslQXKis4HOwCBmCFfZYoyq9iIywQLNQVMvIb%2Bqq2pDBisUTj2fBBpNH7cB3bLKPG3efR",
    "aui": "2776825132",
    "_3dtid": "OkKpyTfSQzlyU+pAFws1Ue+cH45s1skRrxwnXrakd9KWldTkk/Gubb3pHs0ufpBx",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "ea3bca92bf79790a06a13b055908d4b8_1790312046116",
    "_m_h5_tk_enc": "3921e2082b7c45f7f0f72c36ec5788b0",
    "bxuab": "0",
    "sca": "18575fbb",
    "_samesite_flag_": "true",
    "ultraCookieBase": "1k6S5%2BcxkgQpZVbCsyK4ZeavvS%2FOjlVjJC5qBNUjrpFoW5J%2FRHWZeNsxa74KeYQwVGnkQNNa77ctTXC6PxRInUQYe%2FB6YkKBcYhgQLq5cdGUBWwXRcOgpi1jHcGCLcVHGyoZ3dsJCb0zIPLjU1gj1%2Fu3YwJ48wL%2BfsY2gKbLg0I07zDm6uJlCze5Nr6PTjRDVGKWzvEyaHv67egJYrNFbX%2BXAzTqP5fh4VtA7ViWEN14SLQSSzDX0NK2QhiMnzMfQYX0rwjd0c5etdmUR%2BlmX79bee%2F2rXZokASrX4gTCOWAjnvp2knXyNntYilmR2nAGuUZGxA%3D%3D",
    "havana_lgc_exp": "1821406687423",
    "sdkSilent": "1790331487423",
    "havana_sdkSilent": "1790331487423",
    "tfstk": "hJmMkwOp6hGoxpLpqadKjdpdmeKR6tDSUSIOullhgYk7uiL_XrqmTWnT6AEafAZfMPeOVBHe3-1yqPse2AM_cOf2e2uA43C3UZSqgPPUT-NUQGyV0pqUn8EVbrSN86PQ3oPqgPWUY-eu3NPa_pDUO-r4gjr2KkPQ3oPqgo7mMAx3yDqWctPWVZIV0c-bSrK7tgSrx24gagFH6OrUCykbom6fmVDZPjwr_1R85xuntRqDvNrrKqludHWhuZfSdxnhe339NvhET27D_QKE_vHsoMBBwLej8Y4vbOtx4xGnA2I9adioI4ugRTdmALiEz4EGBH9kE5iIE4xhQcmjW093w-c1CYNFfemwKpb-hPyQF7pHKZ_b7Jw3wpvhymaad8NR.",
    "isg": "BPHxvy5aPzWm7JPGArRvrClSAH2L3mVQgwgRwNMG27jX-hFMGy5qIdscHI6cMv2I"
}


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


def get_data(page_num: int, page_size: int) -> list:
    # d.token + "&" + j + "&" + h + "&" + c.data
    token = 'ea3bca92bf79790a06a13b055908d4b8'
    j = 1790304536674
    h = '12574478'
    data_params = {
        "pageNum": page_num,
        "pageSize": page_size,
        "itemLastCount": page_num * page_size,
        "latestHundredItem": "935071146548,784979383182,1075844003512,1069276942279,929629468837,803094764827,1069074239523,984639794053,1041553093736,721732817715,984598735233,840314139055,928750865364,747692967232,1045492810692,1078534137439,1050636498138,664928410758,0,1079861756020,810505644794,1074854561876,952138095293,1082710930547,41294624977,963753441831,1076645039508,993581753148,769079771884,1083932073923,976326040564,952573355082,1014849554431,1077485154445,907827978222,782065080227,681093665849,931559228307,724976325369,17291788029,980989778792,809600268336,815474139424,611067629562,1080417905704,693298018533,1083789752531,788083844609,906546902952,1082086997426",
        "firstPagePVID": "7d11d0b9-b74e-416b-81c1-1fabbc328f10",
        "itemTotal": "900",
        "frontAbId": "427503",
        "isFirstPage": False,
        "myCna": "JgeHItTEvQ4BASQIgkDE9RDx"
    }
    raw_data = {
        "appId": "30986",
        "params": json.dumps(data_params, separators=(',', ':'))
    }
    data = json.dumps(raw_data, separators=(',', ':'))
    # data_1 = '{"appId":"30986","params":"{\\"pageNum\\":2,\\"pageSize\\":25,\\"itemLastCount\\":50,\\"latestHundredItem\\":\\"935071146548,784979383182,1075844003512,1069276942279,929629468837,803094764827,1069074239523,984639794053,1041553093736,721732817715,984598735233,840314139055,928750865364,747692967232,1045492810692,1078534137439,1050636498138,664928410758,0,1079861756020,810505644794,1074854561876,952138095293,1082710930547,41294624977,963753441831,1076645039508,993581753148,769079771884,1083932073923,976326040564,952573355082,1014849554431,1077485154445,907827978222,782065080227,681093665849,931559228307,724976325369,17291788029,980989778792,809600268336,815474139424,611067629562,1080417905704,693298018533,1083789752531,788083844609,906546902952,1082086997426\\",\\"firstPagePVID\\":\\"7d11d0b9-b74e-416b-81c1-1fabbc328f10\\",\\"itemTotal\\":\\"900\\",\\"frontAbId\\":\\"427503\\",\\"isFirstPage\\":false,\\"myCna\\":\\"JgeHItTEvQ4BASQIgkDE9RDx\\"}"}'
    # print(data)
    # print(data_1)
    sign_string = token + "&" + str(j) + "&" + h + "&" + data
    sign = hashlib.md5(sign_string.encode("utf-8")).hexdigest()
    print(sign)

    url = 'https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/'

    params = {
        "jsv": "2.7.2",
        "appKey": "12574478",
        "t": f"{j}",
        "sign": sign,
        "v": "2.0",
        "timeout": "3000",
        "dataType": "jsonp",
        "valueType": "original",
        "jsonpIncPrefix": "pcrecommend",
        "ttid": "1@tbwang_windows_1.0.0#pc",
        "api": "mtop.relationrecommend.WirelessRecommend.recommend",
        "type": "originaljsonp",
        "callback": "mtopjsonppcrecommend23",
        "data": data,
        "bx-ua": "fast-load"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)

    # print(response.text)
    # print(response)
    parsed = parse_jsonp(response.text)
    list_data = extract_list(parsed)
    return list_data


# print(get_data(1, 25))
