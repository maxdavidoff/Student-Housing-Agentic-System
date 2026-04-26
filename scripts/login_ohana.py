from __future__ import annotations

from pathlib import Path

from config.settings import OHANA_LOGIN_URL, OHANA_STORAGE_STATE_PATH
from scrapers.browser import BrowserManager


INSTRUCTIONS = f"""
Ohana login capture
-------------------
1. A headed browser window will open to {OHANA_LOGIN_URL}
2. Log in manually with your own account.
3. Once the site is fully signed in and settled, return to the terminal.
4. Press ENTER to save the authenticated browser state.
""".strip()


def main() -> None:
    print(INSTRUCTIONS)
    with BrowserManager(headless=False) as manager:
        context = manager.new_context()
        page = context.new_page()
        page.goto(OHANA_LOGIN_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        input("\nPress ENTER after you have finished logging in: ")

        state_path = Path(OHANA_STORAGE_STATE_PATH)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(state_path))
        print(f"Saved Ohana auth state to: {state_path}")
        page.close()
        context.close()


if __name__ == "__main__":
    main()
