"""Quickstart example demonstrating Agent-WebPilot core features."""

import os
from agent_webpilot import CDPClient, ChromeLauncher, NativeDOM, PageActions, StealthEngine


def main():
    print("=== Agent-WebPilot Quickstart Demo ===")
    
    # 1. Launch detached Chrome with remote debugging port enabled
    profile_dir = os.path.abspath("./chrome_dev_profile")
    launcher = ChromeLauncher(port=9222, user_data_dir=profile_dir, headless=False)
    
    chrome_exe = launcher.find_chrome_executable()
    if not chrome_exe:
        print("[!] Chrome not found automatically. Please start Chrome with --remote-debugging-port=9222.")
        return

    print(f"[*] Starting Chrome via CDP launcher (Port 9222)...")
    launcher.launch()

    # 2. Connect client & initialize modules
    client = CDPClient(port=9222)
    client.connect()
    
    dom = NativeDOM(client)
    stealth = StealthEngine()
    actions = PageActions(client, dom, stealth)

    try:
        # 3. Navigate to a test page
        target_url = "https://example.com"
        print(f"[*] Navigating to {target_url}...")
        actions.navigate(target_url, wait_selector="h1")

        # 4. Extract page text
        heading = actions.get_text("h1")
        print(f"[+] Page heading: {heading}")

        # 5. Native Setter Form Injection (Vue/React Example)
        # Note: In real SPA applications, this bypasses Virtual DOM event masking:
        # actions.fill_input("input[name='search']", "AI Agent Platform")

        # 6. Capture full screenshot
        screenshot_path = "quickstart_screenshot.png"
        actions.screenshot(screenshot_path)
        print(f"[+] Viewport screenshot saved to: {screenshot_path}")

    finally:
        client.close()
        print("[*] CDP session disconnected. (Detached Chrome keeps running)")


if __name__ == "__main__":
    main()
