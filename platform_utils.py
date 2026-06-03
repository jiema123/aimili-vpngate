#!/usr/bin/env python3
from __future__ import annotations

import platform
import re
import socket
import subprocess
import time

SYSTEM = platform.system()
IS_LINUX = SYSTEM == "Linux"
IS_MACOS = SYSTEM == "Darwin"


def get_physical_interface() -> str | None:
    if IS_MACOS:
        return _get_macos_physical_interface()
    return _get_linux_physical_interface()


def _get_linux_physical_interface() -> str | None:
    try:
        res = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=2)
        if res.returncode != 0:
            return None
        routes = []
        for line in res.stdout.splitlines():
            if line.startswith("default via"):
                parts = line.split()
                try:
                    gw = parts[2]
                    dev = parts[parts.index("dev") + 1]
                    metric = int(parts[parts.index("metric") + 1]) if "metric" in parts else 0
                    routes.append((gw, dev, metric))
                except (ValueError, IndexError):
                    continue
        if routes:
            routes.sort(key=lambda x: x[2])
            for _gw, dev, _metric in routes:
                if not dev.startswith(("tun", "tap", "wg", "ppp")):
                    return dev
            return routes[0][1]
    except Exception:
        pass
    return None


def _get_macos_physical_interface() -> str | None:
    try:
        res = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True, timeout=2)
        if res.returncode != 0:
            return None
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("interface:"):
                dev = line.split(":", 1)[1].strip()
                if dev and not dev.startswith(("utun", "tap", "tun", "ppp")):
                    return dev
    except Exception:
        pass
    return None


def _run_ping(host: str, dev: str | None = None) -> int:
    if IS_MACOS:
        cmd = ["ping", "-c", "1", "-W", "2000", host]
    else:
        cmd = ["ping", "-c", "1", "-W", "2"]
        if dev:
            cmd.extend(["-I", dev])
        cmd.append(host)
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        if res.returncode == 0:
            match = re.search(r"time=([\d.]+)\s*ms", res.stdout)
            if match:
                val = int(float(match.group(1)))
                if val > 0:
                    return val
    except Exception:
        pass
    return 0


def tcp_latency_ms(host: str, port: int, dev: str | None = None) -> int:
    started = time.time()
    af = socket.AF_INET6 if ":" in host else socket.AF_INET
    s = socket.socket(af, socket.SOCK_STREAM)
    try:
        s.settimeout(5)
        if IS_LINUX and dev and hasattr(socket, "SO_BINDTODEVICE"):
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, dev.encode("utf-8"))
            except OSError:
                pass
        s.connect((host, port))
        return max(1, int((time.time() - started) * 1000))
    except OSError:
        return 0
    finally:
        try:
            s.close()
        except Exception:
            pass


def ping_latency_ms(host: str, port: int, fallback_ping: int = 0) -> int:
    dev = get_physical_interface()
    val = _run_ping(host, dev)
    if val > 0:
        return val
    if not IS_MACOS:
        val = _run_ping(host, None)
        if val > 0:
            return val
    val = tcp_latency_ms(host, port, dev)
    if val > 0:
        return val
    return fallback_ping if fallback_ping > 0 else 0
