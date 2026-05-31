# AimiliVPN 🌐

Bilingual: [中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文 (Chinese)

AimiliVPN 是一款基于官方 VPNGate 开放协议的高性能、零依赖 VPN 代理网关。它以纯 Python 标准库编写，内置美观响应式的管理网页，提供智能并发测速、多路由模式、出站代理网关、实时日志等强大功能。

### 📢 官方交流与反馈
[![Telegram](https://img.shields.io/badge/TG交流群-arestemple-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/arestemple)
[![Forum](https://img.shields.io/badge/交流论坛-339936.xyz-orange?style=flat-square&logo=discourse&logoColor=white)](https://339936.xyz)
[![YouTube](https://img.shields.io/badge/视频教程-YouTube-red?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=s-ATfXR8BpI)
[![Email](https://img.shields.io/badge/Bug反馈-yaohunse7@gmail.com-red?style=flat-square&logo=gmail&logoColor=white)](mailto:yaohunse7@gmail.com)

---

### 🚀 一键极速部署 (支持 Debian/Ubuntu/CentOS/Alpine 等 Linux 系统)

在您的 Linux VPS 上以 root 用户执行以下对应命令：

#### 🌟 正式稳定版本 (main 分支)
```bash
bash <(curl -Ls https://raw.githubusercontent.com/baoweise-bot/aimili-vpngate/main/install.sh)
```

#### 🧪 测试开发版本 (bate 分支)
```bash
bash <(curl -Ls https://raw.githubusercontent.com/baoweise-bot/aimili-vpngate/bate/install.sh)
```

> 💡 **小贴士**：部署完成后，终端会输出管理网页的专属链接（含安全后缀）。在终端中输入 `ml` 命令可以随时调出交互式管理菜单。

---

### 🛠️ 核心功能一览
* **一键傻瓜化部署**：全自动配置运行环境，生成随机安全凭证，支持主流 Linux 系统（含轻量化 Alpine）。
* **极简双效网关**：内置代理服务器在单一端口同时提供 HTTP 和 SOCKS5 代理服务（默认端口 `7928`）。
* **精美 Web 管理后台**：现代化暗黑玻璃拟物风格 UI，支持手机、平板、电脑自适应布局。
* **智能测速与连接**：自动并发测试空闲免费节点，支持 **智能自动配置（失效秒级漂移）**、**固定 IP 节点** 和 **固定国家地区** 三种出站路由模式。
* **实时系统诊断**：内置网关服务心跳监测、后台守护线程运行状态跟踪。
* **滚动终端日志**：支持分类过滤、实时滚动、一键复制和导出运行日志。

---

### ⚠️ 小白安装与运行常见问题 (FAQ)

#### 1. 提示 `Cannot allocate tun` 或 `Cannot open tun/tap dev`
* **原因**：VPS 宿主机未启用虚拟网卡（TUN/TAP 设备）。这种情况常见于 LXC 或 OpenVZ 架构的轻量 VPS。
* **解决办法**：请登录您的 VPS 服务商控制面板（如 SolusVM/Proxmox），找到 **Enable TUN/TAP** / **开启 TUN** 选项并启用，然后重启 VPS。如无此选项，请工单联系客服开启。

#### 2. 网页管理后台无法打开（链接超时或拒绝连接）
* **原因 1**：VPS 本身自带防火墙（如 UFW、firewalld 或 iptables）阻断了管理端口（默认 `8787`）或代理端口（默认 `7928`）。
* **解决办法 1**：请在终端放行对应端口：
  * **UFW (Ubuntu/Debian)**: `ufw allow 8787/tcp && ufw allow 7928/tcp`
  * **Firewalld (CentOS/RHEL)**: `firewall-cmd --zone=public --add-port=8787/tcp --permanent && firewall-cmd --zone=public --add-port=7928/tcp --permanent && firewall-cmd --reload`
* **原因 2**：云服务商的“安全组”或“网络访问控制列表 (ACL)”未放行端口。
* **解决办法 2**：登录云服务商控制台（如阿里云、腾讯云、AWS 等），在安全组规则中添加“入站规则”，放行 TCP 协议的 `8787` 和 `7928` 端口。

#### 3. 页面提示 `API Domain Blocked` 且备选节点显示为 0
* **原因**：您的 VPS DNS 解析异常，或者官方 VPNGate 域名遭防火墙拦截污染，导致无法下载节点列表。
* **解决办法**：
  * **设置上游代理**：在网页管理面板中打开“管理员 -> 代理及网络设置”，配置有效的 HTTP/SOCKS5 上游代理，后台会自动通过该代理拉取更新。
  * **修改 DNS 解析器**：在终端修改 `/etc/resolv.conf`，将域名服务器替换为公共 DNS（如 `8.8.8.8` 和 `1.1.1.1`）。

#### 4. VPN 已成功连接，但客户端设置代理后无法上网 (无流量)
* **原因**：部分系统启用了严格的反向路径过滤（`rp_filter`），导致策略路由的入站/出站数据包被系统误判丢弃。
* **解决办法**：在终端输入 `ml` 命令打开交互菜单，工具会自动检测并提示您将 `rp_filter` 修复为宽松模式（值为 `2`）。

---

<a name="english"></a>
## English

AimiliVPN is a high-performance, zero-dependency VPN proxy gateway built entirely using Python's standard library. It parses official VPNGate servers, benchmarks latency, and routes traffic through a built-in dual-protocol (HTTP/SOCKS5) proxy server.

### 📢 Community & Feedback
- **Telegram Group**: [arestemple](https://t.me/arestemple)
- **Discussion Forum**: [339936.xyz](https://339936.xyz)
- **Video Tutorial**: [YouTube Guide](https://www.youtube.com/watch?v=s-ATfXR8BpI)
- **Email Contact**: yaohunse7@gmail.com

---

### 🚀 One-Click Installation

Run the corresponding command on your Linux VPS as root:

#### 🌟 Stable Release (main branch)
```bash
bash <(curl -Ls https://raw.githubusercontent.com/baoweise-bot/aimili-vpngate/main/install.sh)
```

#### 🧪 Beta / Development (bate branch)
```bash
bash <(curl -Ls https://raw.githubusercontent.com/baoweise-bot/aimili-vpngate/bate/install.sh)
```

> 💡 **Quick Note**: Once installed, copy the printed URL from the terminal to access the Web UI. Type the `ml` command in the terminal to summon the interactive CLI management console.

---

### ⚠️ Common Troubleshooting (FAQ)

#### 1. Error: `Cannot allocate tun` or `Cannot open tun/tap dev`
* **Reason**: Virtual network adapter (TUN/TAP device) is disabled. This is common in OpenVZ/LXC VPS instances.
* **Solution**: Enable **TUN/TAP** in your VPS SolusVM/KiwiVM control panel, or submit a support ticket to your hosting provider.

#### 2. Cannot open the Web UI in the browser
* **Reason 1**: The built-in firewall (UFW or firewalld) is blocking ports `8787` (Web UI) and `7928` (Proxy).
* **Solution 1**: Allow the ports in your OS firewall:
  * **UFW**: `ufw allow 8787/tcp && ufw allow 7928/tcp`
  * **Firewalld**: `firewall-cmd --add-port=8787/tcp --permanent && firewall-cmd --add-port=7928/tcp --permanent && firewall-cmd --reload`
* **Reason 2**: Service provider security group blocking ports.
* **Solution 2**: Log in to cloud console (AWS, Aliyun, Oracle Cloud, etc.) and add inbound rules for TCP `8787` and `7928`.

#### 3. "API Domain Blocked" / Candidate nodes pool is empty (0 nodes)
* **Reason**: The official VPNGate domain is blocked or DNS resolution failed on your VPS.
* **Solution**: Add an HTTP/SOCKS5 upstream proxy in the settings panel (Admin -> Proxy Settings), or configure public DNS in `/etc/resolv.conf` (e.g., `nameserver 8.8.8.8`).