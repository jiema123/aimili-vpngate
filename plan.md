# macOS compatibility plan

## Goal

Add first-class macOS support while preserving the current Linux VPS behavior.

The initial macOS target is a local developer / local proxy mode:

- start the Python manager on macOS
- serve the Web UI
- fetch and benchmark VPNGate nodes
- start OpenVPN when installed
- expose the local HTTP/SOCKS5 proxy on `127.0.0.1:7928`

Linux-specific routing, iptables, rp_filter repair, and public gateway behavior remain Linux-only unless a safe macOS equivalent is implemented later.

## Scope

### Phase 1: platform detection and safe fallbacks

- Add `platform_utils.py`.
- Detect Linux vs macOS with `platform.system()`.
- Move platform-specific interface and ping helpers into this module.
- Keep Linux behavior unchanged.
- Add macOS implementations using `route -n get default` and macOS-compatible `ping` arguments.
- Disable Linux-only `SO_BINDTODEVICE` on macOS.

### Phase 2: installer compatibility

- Update `install.sh` to detect `Darwin` before reading `/etc/os-release`.
- On macOS, require Homebrew for dependency installation.
- Install or verify `python3` and `openvpn`.
- Clone or update the repository into `/opt/aimilivpn` when running as root, or `$HOME/.aimilivpn` when not root.
- Create a `launchd` plist instead of systemd/OpenRC.
- Keep the existing Linux installation flow unchanged.

### Phase 3: service behavior

- On Linux, continue to create `aimilivpn.service` or OpenRC service.
- On macOS, create `com.aimilivpn.manager.plist`.
- Prefer a user LaunchAgent when not root.
- Prefer a system LaunchDaemon when running as root.
- Write environment overrides to a small shell/env file only where launchd can consume them safely.

### Phase 4: documentation and operator guidance

- Update README with a macOS section.
- Clearly label macOS support as local-proxy mode first.
- Document required permissions for OpenVPN.
- Warn that public proxy exposure is not recommended on macOS.

## Implementation checklist

- [ ] Add `platform_utils.py`.
- [ ] Refactor `vpn_utils.get_physical_interface()` to call `platform_utils.get_physical_interface()`.
- [ ] Refactor `vpn_utils.ping_latency_ms()` to call `platform_utils.ping_latency_ms()`.
- [ ] Ensure TCP latency checks do not use Linux-only socket options on macOS.
- [ ] Update `install.sh` with a Darwin branch.
- [ ] Generate a launchd plist for macOS.
- [ ] Add README macOS instructions.
- [ ] Smoke test Linux import paths.
- [ ] Smoke test macOS command generation by static review.

## Non-goals for the first macOS version

- Do not implement pfctl NAT rules.
- Do not implement macOS global route hijacking.
- Do not expose the local proxy publicly by default.
- Do not replace Tunnelblick/OpenVPN Connect as a full GUI VPN client.

## Acceptance criteria

### Linux

- Existing Linux install commands still work.
- Existing systemd/OpenRC service behavior is unchanged.
- Existing Linux node tests still use Linux interface binding where supported.

### macOS

- `install.sh` no longer exits as unsupported on macOS.
- The installer can install dependencies with Homebrew or print clear instructions.
- The manager can be started with launchd.
- `vpn_utils` no longer assumes `ip route`, Linux `ping -I`, or `SO_BINDTODEVICE` on macOS.
- Web UI and local proxy defaults remain bound to safe local addresses unless explicitly changed.
