#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
import threading
from pathlib import Path
from typing import Any

from platform_utils import get_physical_interface, ping_latency_ms, tcp_latency_ms

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "vpngate_data"
IP_CACHE_FILE = DATA_DIR / "ip_cache.json"

ip_cache_lock = threading.RLock()

COUNTRY_TRANSLATIONS = {
    "Japan": "日本",
    "Korea Republic of": "韩国",
    "Korea": "韩国",
    "Republic of Korea": "韩国",
    "Thailand": "泰国",
    "United States": "美国",
    "United Kingdom": "英国",
    "Russian Federation": "俄罗斯",
    "Russian": "俄罗斯",
    "Viet Nam": "越南",
    "Vietnam": "越南",
    "China": "中国",
    "Taiwan": "台湾",
    "Taiwan Province of China": "台湾",
    "Hong Kong": "香港",
    "Singapore": "新加坡",
    "Malaysia": "马来西亚",
    "Indonesia": "印度尼西亚",
    "India": "印度",
    "Philippines": "菲律宾",
    "Australia": "澳大利亚",
    "New Zealand": "新西兰",
    "Canada": "加拿大",
    "Ukraine": "乌克兰",
    "France": "法国",
    "Germany": "德国",
    "Netherlands": "荷兰",
    "Sweden": "瑞典",
    "Norway": "挪威",
    "Spain": "西班牙",
    "Turkey": "土耳其",
    "South Africa": "南非",
    "Brazil": "巴西",
    "Argentina": "阿根廷",
    "Chile": "智利",
    "Mexico": "墨西哥",
    "Egypt": "埃及",
    "Romania": "罗马尼亚",
    "Poland": "波兰",
    "Kazakhstan": "哈萨克斯坦",
    "Georgia": "格鲁吉亚",
    "Mongolia": "蒙古",
    "Saudi Arabia": "沙特阿拉伯",
    "Iran": "伊朗",
    "Iraq": "伊拉克",
    "Colombia": "哥伦比亚",
    "Cambodia": "柬埔寨",
    "Ireland": "爱尔兰",
    "Italy": "意大利",
    "Switzerland": "瑞士",
    "Belgium": "比利时",
    "Austria": "奥地利",
    "Denmark": "丹麦",
    "Finland": "芬兰",
    "Portugal": "葡萄牙",
    "Greece": "希腊",
    "Czech Republic": "捷克",
    "Hungary": "匈牙利",
    "Israel": "以色列",
    "United Arab Emirates": "阿联酋",
    "UAE": "阿联酋",
    "Macao": "澳门",
    "Macau": "澳门",
    "Iceland": "冰岛",
    "Luxembourg": "卢森堡",
}


def get_upstream_proxy() -> tuple[str | None, str | None, int | None]:
    socks_env = os.environ.get("OPENVPN_UPSTREAM_SOCKS")
    if socks_env:
        if "://" in socks_env:
            parsed = urllib.parse.urlsplit(socks_env)
            if parsed.hostname and parsed.port:
                return "socks", parsed.hostname, parsed.port
        else:
            parts = socks_env.split(":")
            if len(parts) == 2:
                return "socks", parts[0], int(parts[1])
            if len(parts) == 1:
                return "socks", parts[0], 10808

    http_env = os.environ.get("OPENVPN_UPSTREAM_HTTP")
    if http_env:
        if "://" in http_env:
            parsed = urllib.parse.urlsplit(http_env)
            if parsed.hostname and parsed.port:
                return "http", parsed.hostname, parsed.port
        else:
            parts = http_env.split(":")
            if len(parts) == 2:
                return "http", parts[0], int(parts[1])
            if len(parts) == 1:
                return "http", parts[0], 10808

    for env_name in ["http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"]:
        val = os.environ.get(env_name)
        if not val:
            continue
        if "://" in val:
            parsed = urllib.parse.urlsplit(val)
            ptype = "socks" if parsed.scheme.startswith("socks") else "http"
            if parsed.hostname and parsed.port:
                return ptype, parsed.hostname, parsed.port
        else:
            parts = val.split(":")
            if len(parts) == 2:
                return "http", parts[0], int(parts[1])
    return None, None, None


def is_config_tcp(config_text: str) -> bool:
    for line in config_text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        parts = line.split()
        if parts[0].lower() == "proto" and len(parts) >= 2 and "tcp" in parts[1].lower():
            return True
        if parts[0].lower() == "remote" and len(parts) >= 4 and "tcp" in parts[3].lower():
            return True
    return False


def parse_remote(config_text: str, fallback_ip: str = "") -> tuple[str, int, str]:
    remote_host = fallback_ip
    remote_port = 0
    proto = "unknown"
    for raw_line in config_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        parts = line.split()
        if parts[0].lower() == "proto" and len(parts) >= 2:
            proto = parts[1].lower()
        elif parts[0].lower() == "remote" and len(parts) >= 3:
            remote_host = parts[1]
            remote_port = int(parts[2]) if parts[2].isdigit() else 0
    return remote_host, remote_port, proto


def check_and_fix_dns() -> None:
    # macOS manages DNS via SystemConfiguration; avoid editing /etc/resolv.conf there.
    import platform
    import socket
    if platform.system() == "Darwin":
        return
    try:
        socket.getaddrinfo("www.vpngate.net", 443)
        return
    except (socket.gaierror, OSError):
        pass
    for ip, port, af in [("8.8.8.8", 53, socket.AF_INET), ("1.1.1.1", 53, socket.AF_INET)]:
        s = socket.socket(af, socket.SOCK_DGRAM)
        try:
            s.settimeout(2)
            s.connect((ip, port))
            resolv_file = Path("/etc/resolv.conf")
            if resolv_file.exists():
                content = resolv_file.read_text(encoding="utf-8", errors="replace")
                if "nameserver 1.1.1.1" not in content and "nameserver 8.8.8.8" not in content:
                    with open("/etc/resolv.conf", "a", encoding="utf-8") as f:
                        f.write("\nnameserver 1.1.1.1\nnameserver 8.8.8.8\n")
            return
        except Exception:
            pass
        finally:
            try:
                s.close()
            except Exception:
                pass


def load_ip_cache() -> dict[str, dict[str, Any]]:
    with ip_cache_lock:
        try:
            if IP_CACHE_FILE.exists():
                return json.loads(IP_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}


def save_ip_cache(cache: dict[str, dict[str, Any]]) -> None:
    with ip_cache_lock:
        try:
            DATA_DIR.mkdir(exist_ok=True)
            IP_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


def enrich_ip_info(nodes: list[dict[str, Any]]) -> None:
    return


def diagnose_api_failure(api_url: str = "https://www.vpngate.net/api/iphone/") -> tuple[int, str]:
    return 1010, "[ERR_API_CHECK_SKIPPED] API 诊断在兼容层精简版本中未执行，请查看主日志中的网络错误。"


def diagnose_openvpn_failure(log_tail: list[str]) -> tuple[int, str]:
    joined_log = "\n".join(log_tail).lower()
    if "command not found" in joined_log or "no such file or directory" in joined_log:
        return 2001, "[ERR_OVPN_CMD_NOT_FOUND] 未找到 openvpn 命令。请安装 OpenVPN 或检查 PATH。"
    if "cannot allocate tun" in joined_log or "cannot open tun/tap" in joined_log or "utun" in joined_log:
        return 2009, "[ERR_OVPN_TUN_NOT_AVAILABLE] 无法创建虚拟网卡。Linux 请启用 TUN；macOS 请确认 OpenVPN 有管理员权限。"
    if "auth_failed" in joined_log or "authentication failed" in joined_log:
        return 2005, "[ERR_OVPN_AUTH_FAILED] OpenVPN 身份验证失败，节点可能已失效。"
    if "cannot resolve host address" in joined_log:
        return 2002, "[ERR_OVPN_DNS_FAILED] OpenVPN 无法解析节点域名。"
    if "connection timed out" in joined_log or "tls key negotiation failed" in joined_log:
        return 2003, "[ERR_OVPN_CONNECT_TIMEOUT] OpenVPN 连接超时，节点可能不可达。"
    return 2999, "[ERR_OVPN_UNKNOWN] OpenVPN 启动失败，请查看详细日志。"
