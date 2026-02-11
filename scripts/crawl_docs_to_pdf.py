#!/usr/bin/env python3
"""
Lena Doc Crawler — Print every documentation page to PDF
Targets: OpenCode, OpenClaw, Oh My OpenCode
Uses Playwright (Chromium) headless browser for accurate rendering
"""

import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# ── Configuration ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent / "docs"

# OpenCode docs (33 pages)
OPENCODE_PAGES = [
    "https://opencode.ai/docs",
    "https://opencode.ai/docs/config",
    "https://opencode.ai/docs/providers",
    "https://opencode.ai/docs/network",
    "https://opencode.ai/docs/enterprise",
    "https://opencode.ai/docs/troubleshooting",
    "https://opencode.ai/docs/windows-wsl",
    "https://opencode.ai/docs/tui",
    "https://opencode.ai/docs/cli",
    "https://opencode.ai/docs/web",
    "https://opencode.ai/docs/ide",
    "https://opencode.ai/docs/zen",
    "https://opencode.ai/docs/share",
    "https://opencode.ai/docs/github",
    "https://opencode.ai/docs/gitlab",
    "https://opencode.ai/docs/tools",
    "https://opencode.ai/docs/rules",
    "https://opencode.ai/docs/agents",
    "https://opencode.ai/docs/models",
    "https://opencode.ai/docs/themes",
    "https://opencode.ai/docs/keybinds",
    "https://opencode.ai/docs/commands",
    "https://opencode.ai/docs/formatters",
    "https://opencode.ai/docs/permissions",
    "https://opencode.ai/docs/lsp",
    "https://opencode.ai/docs/mcp-servers",
    "https://opencode.ai/docs/acp",
    "https://opencode.ai/docs/skills",
    "https://opencode.ai/docs/custom-tools",
    "https://opencode.ai/docs/sdk",
    "https://opencode.ai/docs/server",
    "https://opencode.ai/docs/plugins",
    "https://opencode.ai/docs/ecosystem",
]

# OpenClaw docs (200+ pages)
OPENCLAW_PAGES = [
    # Get started
    "https://docs.openclaw.ai/",
    "https://docs.openclaw.ai/start/showcase",
    "https://docs.openclaw.ai/concepts/features",
    "https://docs.openclaw.ai/start/getting-started",
    "https://docs.openclaw.ai/start/onboarding-overview",
    "https://docs.openclaw.ai/start/wizard",
    "https://docs.openclaw.ai/start/onboarding",
    "https://docs.openclaw.ai/start/openclaw",
    # Install
    "https://docs.openclaw.ai/install",
    "https://docs.openclaw.ai/install/installer",
    "https://docs.openclaw.ai/install/docker",
    "https://docs.openclaw.ai/install/nix",
    "https://docs.openclaw.ai/install/ansible",
    "https://docs.openclaw.ai/install/bun",
    "https://docs.openclaw.ai/install/updating",
    "https://docs.openclaw.ai/install/migrating",
    "https://docs.openclaw.ai/install/uninstall",
    "https://docs.openclaw.ai/install/fly",
    "https://docs.openclaw.ai/install/hetzner",
    "https://docs.openclaw.ai/install/gcp",
    "https://docs.openclaw.ai/install/macos-vm",
    "https://docs.openclaw.ai/install/exe-dev",
    "https://docs.openclaw.ai/install/railway",
    "https://docs.openclaw.ai/install/render",
    "https://docs.openclaw.ai/install/northflank",
    "https://docs.openclaw.ai/install/development-channels",
    "https://docs.openclaw.ai/install/node",
    # Channels
    "https://docs.openclaw.ai/channels",
    "https://docs.openclaw.ai/channels/whatsapp",
    "https://docs.openclaw.ai/channels/telegram",
    "https://docs.openclaw.ai/channels/discord",
    "https://docs.openclaw.ai/channels/irc",
    "https://docs.openclaw.ai/channels/slack",
    "https://docs.openclaw.ai/channels/feishu",
    "https://docs.openclaw.ai/channels/googlechat",
    "https://docs.openclaw.ai/channels/mattermost",
    "https://docs.openclaw.ai/channels/signal",
    "https://docs.openclaw.ai/channels/imessage",
    "https://docs.openclaw.ai/channels/msteams",
    "https://docs.openclaw.ai/channels/line",
    "https://docs.openclaw.ai/channels/matrix",
    "https://docs.openclaw.ai/channels/zalo",
    "https://docs.openclaw.ai/channels/zalouser",
    "https://docs.openclaw.ai/channels/pairing",
    "https://docs.openclaw.ai/channels/group-messages",
    "https://docs.openclaw.ai/channels/groups",
    "https://docs.openclaw.ai/channels/broadcast-groups",
    "https://docs.openclaw.ai/channels/channel-routing",
    "https://docs.openclaw.ai/channels/location",
    "https://docs.openclaw.ai/channels/troubleshooting",
    # Agents / Concepts
    "https://docs.openclaw.ai/concepts/architecture",
    "https://docs.openclaw.ai/concepts/agent",
    "https://docs.openclaw.ai/concepts/agent-loop",
    "https://docs.openclaw.ai/concepts/system-prompt",
    "https://docs.openclaw.ai/concepts/context",
    "https://docs.openclaw.ai/concepts/agent-workspace",
    "https://docs.openclaw.ai/concepts/oauth",
    "https://docs.openclaw.ai/start/bootstrapping",
    "https://docs.openclaw.ai/concepts/session",
    "https://docs.openclaw.ai/concepts/sessions",
    "https://docs.openclaw.ai/concepts/session-pruning",
    "https://docs.openclaw.ai/concepts/session-tool",
    "https://docs.openclaw.ai/concepts/memory",
    "https://docs.openclaw.ai/concepts/compaction",
    "https://docs.openclaw.ai/concepts/multi-agent",
    "https://docs.openclaw.ai/concepts/presence",
    "https://docs.openclaw.ai/concepts/messages",
    "https://docs.openclaw.ai/concepts/streaming",
    "https://docs.openclaw.ai/concepts/retry",
    "https://docs.openclaw.ai/concepts/queue",
    "https://docs.openclaw.ai/concepts/timezone",
    "https://docs.openclaw.ai/concepts/models",
    "https://docs.openclaw.ai/concepts/model-failover",
    # Tools
    "https://docs.openclaw.ai/tools",
    "https://docs.openclaw.ai/tools/lobster",
    "https://docs.openclaw.ai/tools/llm-task",
    "https://docs.openclaw.ai/tools/exec",
    "https://docs.openclaw.ai/tools/web",
    "https://docs.openclaw.ai/tools/apply-patch",
    "https://docs.openclaw.ai/tools/elevated",
    "https://docs.openclaw.ai/tools/thinking",
    "https://docs.openclaw.ai/tools/reactions",
    "https://docs.openclaw.ai/tools/browser",
    "https://docs.openclaw.ai/tools/browser-login",
    "https://docs.openclaw.ai/tools/chrome-extension",
    "https://docs.openclaw.ai/tools/browser-linux-troubleshooting",
    "https://docs.openclaw.ai/tools/agent-send",
    "https://docs.openclaw.ai/tools/subagents",
    "https://docs.openclaw.ai/tools/multi-agent-sandbox-tools",
    "https://docs.openclaw.ai/tools/slash-commands",
    "https://docs.openclaw.ai/tools/skills",
    "https://docs.openclaw.ai/tools/skills-config",
    "https://docs.openclaw.ai/tools/clawhub",
    "https://docs.openclaw.ai/tools/plugin",
    # Plugins
    "https://docs.openclaw.ai/plugins/voice-call",
    "https://docs.openclaw.ai/plugins/zalouser",
    # Automation
    "https://docs.openclaw.ai/automation/hooks",
    "https://docs.openclaw.ai/automation/cron-jobs",
    "https://docs.openclaw.ai/automation/cron-vs-heartbeat",
    "https://docs.openclaw.ai/automation/troubleshooting",
    "https://docs.openclaw.ai/automation/webhook",
    "https://docs.openclaw.ai/automation/gmail-pubsub",
    "https://docs.openclaw.ai/automation/poll",
    "https://docs.openclaw.ai/automation/auth-monitoring",
    "https://docs.openclaw.ai/hooks/soul-evil",
    # Nodes
    "https://docs.openclaw.ai/nodes",
    "https://docs.openclaw.ai/nodes/troubleshooting",
    "https://docs.openclaw.ai/nodes/images",
    "https://docs.openclaw.ai/nodes/audio",
    "https://docs.openclaw.ai/nodes/camera",
    "https://docs.openclaw.ai/nodes/talk",
    "https://docs.openclaw.ai/nodes/voicewake",
    "https://docs.openclaw.ai/nodes/location-command",
    # Providers / Models
    "https://docs.openclaw.ai/providers",
    "https://docs.openclaw.ai/providers/models",
    "https://docs.openclaw.ai/providers/anthropic",
    "https://docs.openclaw.ai/providers/openai",
    "https://docs.openclaw.ai/providers/openrouter",
    "https://docs.openclaw.ai/providers/litellm",
    "https://docs.openclaw.ai/providers/bedrock",
    "https://docs.openclaw.ai/providers/vercel-ai-gateway",
    "https://docs.openclaw.ai/providers/moonshot",
    "https://docs.openclaw.ai/providers/minimax",
    "https://docs.openclaw.ai/providers/opencode",
    "https://docs.openclaw.ai/providers/glm",
    "https://docs.openclaw.ai/providers/zai",
    "https://docs.openclaw.ai/providers/synthetic",
    "https://docs.openclaw.ai/providers/qianfan",
    # Platforms
    "https://docs.openclaw.ai/platforms",
    "https://docs.openclaw.ai/platforms/macos",
    "https://docs.openclaw.ai/platforms/linux",
    "https://docs.openclaw.ai/platforms/windows",
    "https://docs.openclaw.ai/platforms/android",
    "https://docs.openclaw.ai/platforms/ios",
    "https://docs.openclaw.ai/platforms/mac/dev-setup",
    "https://docs.openclaw.ai/platforms/mac/menu-bar",
    "https://docs.openclaw.ai/platforms/mac/voicewake",
    "https://docs.openclaw.ai/platforms/mac/voice-overlay",
    "https://docs.openclaw.ai/platforms/mac/webchat",
    "https://docs.openclaw.ai/platforms/mac/canvas",
    "https://docs.openclaw.ai/platforms/mac/child-process",
    "https://docs.openclaw.ai/platforms/mac/health",
    "https://docs.openclaw.ai/platforms/mac/icon",
    "https://docs.openclaw.ai/platforms/mac/logging",
    "https://docs.openclaw.ai/platforms/mac/permissions",
    "https://docs.openclaw.ai/platforms/mac/remote",
    "https://docs.openclaw.ai/platforms/mac/signing",
    "https://docs.openclaw.ai/platforms/mac/release",
    "https://docs.openclaw.ai/platforms/mac/bundled-gateway",
    "https://docs.openclaw.ai/platforms/mac/xpc",
    "https://docs.openclaw.ai/platforms/mac/skills",
    "https://docs.openclaw.ai/platforms/mac/peekaboo",
    # Gateway & Ops
    "https://docs.openclaw.ai/gateway",
    "https://docs.openclaw.ai/gateway/configuration",
    "https://docs.openclaw.ai/gateway/configuration-reference",
    "https://docs.openclaw.ai/gateway/configuration-examples",
    "https://docs.openclaw.ai/gateway/authentication",
    "https://docs.openclaw.ai/gateway/health",
    "https://docs.openclaw.ai/gateway/heartbeat",
    "https://docs.openclaw.ai/gateway/doctor",
    "https://docs.openclaw.ai/gateway/logging",
    "https://docs.openclaw.ai/gateway/gateway-lock",
    "https://docs.openclaw.ai/gateway/background-process",
    "https://docs.openclaw.ai/gateway/multiple-gateways",
    "https://docs.openclaw.ai/gateway/protocol",
    "https://docs.openclaw.ai/gateway/bridge-protocol",
    "https://docs.openclaw.ai/gateway/openai-http-api",
    "https://docs.openclaw.ai/gateway/tools-invoke-http-api",
    "https://docs.openclaw.ai/gateway/cli-backends",
    "https://docs.openclaw.ai/gateway/local-models",
    "https://docs.openclaw.ai/gateway/network-model",
    "https://docs.openclaw.ai/gateway/pairing",
    "https://docs.openclaw.ai/gateway/discovery",
    "https://docs.openclaw.ai/gateway/bonjour",
    "https://docs.openclaw.ai/gateway/remote",
    "https://docs.openclaw.ai/gateway/remote-gateway-readme",
    "https://docs.openclaw.ai/gateway/tailscale",
    "https://docs.openclaw.ai/security/formal-verification",
    # Web UI
    "https://docs.openclaw.ai/web",
    "https://docs.openclaw.ai/web/control-ui",
    "https://docs.openclaw.ai/web/dashboard",
    "https://docs.openclaw.ai/web/webchat",
    "https://docs.openclaw.ai/web/tui",
    # CLI reference
    "https://docs.openclaw.ai/cli",
    # Reference
    "https://docs.openclaw.ai/reference/rpc",
    "https://docs.openclaw.ai/reference/device-models",
    "https://docs.openclaw.ai/reference/templates/AGENTS",
    "https://docs.openclaw.ai/reference/templates/BOOT",
    "https://docs.openclaw.ai/reference/templates/BOOTSTRAP",
    "https://docs.openclaw.ai/reference/templates/HEARTBEAT",
    "https://docs.openclaw.ai/reference/templates/IDENTITY",
    "https://docs.openclaw.ai/reference/templates/SOUL",
    "https://docs.openclaw.ai/reference/templates/TOOLS",
    "https://docs.openclaw.ai/reference/templates/USER",
    "https://docs.openclaw.ai/reference/wizard",
    "https://docs.openclaw.ai/reference/token-use",
    "https://docs.openclaw.ai/reference/credits",
    "https://docs.openclaw.ai/reference/test",
    "https://docs.openclaw.ai/reference/session-management-compaction",
    # Help
    "https://docs.openclaw.ai/help/troubleshooting",
    "https://docs.openclaw.ai/help/faq",
    "https://docs.openclaw.ai/start/lore",
    "https://docs.openclaw.ai/help/environment",
    "https://docs.openclaw.ai/help/debugging",
    "https://docs.openclaw.ai/help/testing",
    "https://docs.openclaw.ai/help/scripts",
    "https://docs.openclaw.ai/start/setup",
    "https://docs.openclaw.ai/start/hubs",
    "https://docs.openclaw.ai/ci",
]

# Oh My OpenCode (GitHub pages)
OH_MY_OPENCODE_PAGES = [
    "https://github.com/code-yeongyu/oh-my-opencode",
    "https://github.com/code-yeongyu/oh-my-opencode/blob/main/README.md",
]


def url_to_filename(url: str) -> str:
    """Convert URL to a safe filename."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    # Replace slashes with double underscores
    name = re.sub(r"[/\\]", "__", path)
    # Remove unsafe chars
    name = re.sub(r"[^a-zA-Z0-9_\-.]", "_", name)
    return name


async def print_page_to_pdf(page, url: str, output_dir: Path) -> bool:
    """Navigate to URL and print to PDF."""
    filename = url_to_filename(url) + ".pdf"
    filepath = output_dir / filename

    if filepath.exists():
        print(f"  ⏭ SKIP (exists): {filename}")
        return True

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        # Wait for content to render
        await page.wait_for_timeout(2000)

        # Remove nav/sidebar for cleaner PDF
        await page.evaluate("""
            () => {
                const selectors = [
                    'nav', 'header', 'footer',
                    '[class*="sidebar"]', '[class*="toc"]',
                    '[class*="nav"]', '[id*="sidebar"]'
                ];
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        // Only remove if it's not the main content
                        if (!el.querySelector('article') && !el.querySelector('main')) {
                            el.style.display = 'none';
                        }
                    });
                });
                // Expand main content
                const main = document.querySelector('main') || document.querySelector('article');
                if (main) {
                    main.style.maxWidth = '100%';
                    main.style.width = '100%';
                    main.style.margin = '0';
                    main.style.padding = '20px';
                }
            }
        """)

        await page.pdf(
            path=str(filepath),
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
        )
        print(f"  ✅ {filename} ({filepath.stat().st_size // 1024}KB)")
        return True
    except Exception as e:
        print(f"  ❌ FAIL {url}: {e}")
        return False


async def crawl_site(browser, name: str, urls: list[str]):
    """Crawl all pages of a site and save PDFs."""
    output_dir = BASE_DIR / name / "pdf"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"📚 Crawling {name} — {len(urls)} pages")
    print(f"{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1280, "height": 1024},
        locale="en-US",
    )
    page = await context.new_page()

    success = 0
    failed = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        if await print_page_to_pdf(page, url, output_dir):
            success += 1
        else:
            failed += 1

    await context.close()
    print(f"\n✅ {name}: {success} saved, {failed} failed out of {len(urls)} total")
    return success, failed


async def main():
    from playwright.async_api import async_playwright

    print("🦞 Lena Doc Crawler — Starting")
    print(f"📁 Output: {BASE_DIR}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        total_success = 0
        total_failed = 0

        # Crawl all 3 sites
        for name, urls in [
            ("opencode", OPENCODE_PAGES),
            ("openclaw", OPENCLAW_PAGES),
            ("oh-my-opencode", OH_MY_OPENCODE_PAGES),
        ]:
            s, f = await crawl_site(browser, name, urls)
            total_success += s
            total_failed += f

        await browser.close()

    print(f"\n{'='*60}")
    print(f"🏁 DONE: {total_success} PDFs saved, {total_failed} failed")
    print(f"📁 All PDFs in: {BASE_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
