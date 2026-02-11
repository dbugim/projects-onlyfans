from datetime import date, timedelta, datetime
import sys
import os
import time
import pyautogui
import pandas as pd
import subprocess
import atexit
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page


# region Script to help build the executable with PyInstaller
try:
    # For PyInstaller executable
    sys.path.append(os.path.join(sys._MEIPASS, "repository"))
except Exception:
    # For development
    sys.path.append(str(Path(__file__).resolve().parent.parent / "repository"))

# Global variables to keep references
playwright_instance = None
browser_context = None
# endregion

def cleanup_playwright():
    """Function to clean up Playwright resources on exit"""
    global playwright_instance, browser_context
    try:
        if browser_context:
            browser_context.close()
        if playwright_instance:
            playwright_instance.stop()
    except:
        pass

# Register cleanup function to be called on exit
atexit.register(cleanup_playwright)

def open_chrome_with_profile():
    """
    Opens a Google Chrome instance with all profile data,
    keeping the session active indefinitely.
    """
    global playwright_instance, browser_context

    # Install Playwright if necessary
    #print("Checking Playwright installation...")
    subprocess.run(["playwright", "install"], shell=True, capture_output=True)
    subprocess.run(["playwright", "install", "chromium"], shell=True, capture_output=True)

    # Chrome profile path
    profile_path = r"C:\Users\danie\AppData\Local\Google\Chrome\User Data\Default"

    # Check if the profile directory exists
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile directory not found: {profile_path}")

    print("Warning: Make sure Chrome is completely closed")

    try:
        #print("Starting Playwright...")
        # IMPORTANT: Do NOT use 'with' here to keep the session active
        playwright_instance = sync_playwright().start()

        #print("Launching Chrome with profile...")

        # Launch Chrome with specific profile
        browser_context = playwright_instance.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=[
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-sync',
                '--disable-web-security',
                '--disable-features=msRealtimeCommunication,TranslateUI',
                '--remote-debugging-port=0'
            ],
            timeout=30000
        )

        #print("Browser launched successfully!")

        # Open new tab
        page = browser_context.new_page()
        #print("New tab opened")

        # Navigate to the page
        #print("Navigating to OnlyFans messages page...")
        page.goto("https://onlyfans.com", timeout=15000)

        #print("Chrome opened successfully with all profile data!")
        #print("You can now interact with cookies, history, and saved profile data")

        return browser_context, page

    except Exception as e:
        print(f"Error opening Chrome: {e}")
        print("Troubleshooting tips:")
        print("1. Make sure Chrome is completely closed (check Task Manager)")
        print("2. Run this script as administrator")
        print("3. Try using a different profile path if necessary")

        # Clean up resources in case of error
        cleanup_playwright()
        raise

def keep_browser_alive():
    """
    Keeps the browser active indefinitely.
    Call this function after open_chrome_with_profile() if you want to keep the browser open.
    """
    try:
        print("Keeping browser active... (Press Ctrl+C to terminate)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing browser...")
        cleanup_playwright()

def insert_username(page):
    """
    Attempt to find the username input field and insert 'hacksimone29@gmail.com'.
    Updated to target standard Google login inputs (specifically #input-13).
    """
    try:
        # List of selectors to try (updated with new ID #input-13 and standard attributes)
        selectors = [
            # 1. Direct ID match (Most specific based on your update)
            "#input-13",
            "input#input-13",

            # 2. Standard Google Email Input attributes (High reliability)
            "input[type='email'][name='email']",
            "input[name='email']",
            "input[type='email']",

            # 3. XPath specific to the new ID
            "//*[@id='input-13']",

            # 4. XPath general for email inputs
            "//input[@type='email' and @name='email']",
            "//input[@name='email']",

            # 5. Legacy/Shadow DOM selectors (Kept just in case the structure reverts or varies)
            'document.querySelector("#privacy-web-auth").shadowRoot.querySelector("input[type=\'email\']")',
            'document.querySelector("#privacy-web-auth").shadowRoot.querySelector("#floating-input-jnygnm9")'
        ]

        # Try each selector
        for selector in selectors:
            try:
                # Handle different selector types
                if selector.startswith("document.querySelector"):
                    # JavaScript selector (handles shadow DOM)
                    input_inserted = page.evaluate(f'''(text) => {{
                        try {{
                            const input = {selector};
                            if (input) {{
                                input.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                                input.focus();
                                input.value = text;
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                                return true;
                            }}
                        }} catch(e) {{
                            // Silent fail for this selector
                        }}
                        return false;
                    }}''', "hacksimone29@gmail.com")
                    if input_inserted:
                        print("✓ Username inserted successfully with JS/Shadow selector")
                        return True

                elif selector.startswith('/'):
                    # XPath selector
                    xpath_elements = page.locator(f"xpath={selector}")
                    if xpath_elements.count() > 0:
                        try:
                            # Force visibility just in case
                            page.evaluate(f'''(selector) => {{
                                const element = document.evaluate(
                                    `{selector}`,
                                    document,
                                    null,
                                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                                    null
                                ).singleNodeValue;
                                if (element) {{
                                    element.style.opacity = '1';
                                    element.style.visibility = 'visible';
                                    element.style.display = 'block';
                                }}
                            }}''', selector)

                            xpath_elements.first.scroll_into_view_if_needed()
                            xpath_elements.first.click() # Click ensures focus
                            xpath_elements.first.fill("hacksimone29@gmail.com")
                            print(f"✓ Username inserted successfully with XPath: {selector}")
                            return True
                        except Exception as e:
                            print(f"XPath insert failed: {str(e)}")

                else:
                    # CSS selector
                    css_elements = page.locator(selector)
                    if css_elements.count() > 0:
                        try:
                            # Force visibility
                            page.evaluate(f'''(selector) => {{
                                const element = document.querySelector(selector);
                                if (element) {{
                                    element.style.opacity = '1';
                                    element.style.visibility = 'visible';
                                    element.style.display = 'block';
                                }}
                            }}''', selector)

                            css_elements.first.scroll_into_view_if_needed()
                            css_elements.first.click() # Click ensures focus
                            css_elements.first.fill("hacksimone29@gmail.com")
                            print(f"✓ Username inserted successfully with CSS selector: {selector}")
                            return True
                        except Exception as e:
                            print(f"CSS selector insert failed: {str(e)}")

            except Exception as e:
                # Continue to next selector if one fails
                continue

        # Fallback JavaScript approach with comprehensive search (Updated for #input-13)
        print("Trying JavaScript fallback approach for username input...")
        fallback_inserted = page.evaluate('''(text) => {
            // 1. Try Direct ID first (Fastest)
            const directInput = document.getElementById('input-13');
            if (directInput) {
                directInput.scrollIntoView({behavior: 'smooth', block: 'center'});
                directInput.focus();
                directInput.value = text;
                directInput.dispatchEvent(new Event('input', { bubbles: true }));
                directInput.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }

            // 2. Try Standard Name/Type attributes
            const standardInput = document.querySelector('input[name="email"]') || document.querySelector('input[type="email"]');
            if (standardInput) {
                standardInput.scrollIntoView({behavior: 'smooth', block: 'center'});
                standardInput.focus();
                standardInput.value = text;
                standardInput.dispatchEvent(new Event('input', { bubbles: true }));
                standardInput.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }

            // 3. Try Shadow DOM (Legacy support)
            const shadowHost = document.querySelector("#privacy-web-auth");
            if (shadowHost && shadowHost.shadowRoot) {
                const shadowInput = shadowHost.shadowRoot.querySelector('input[type="email"]');
                if (shadowInput) {
                    shadowInput.value = text;
                    shadowInput.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
            }

            return false;
        }''', "hacksimone29@gmail.com")

        if fallback_inserted:
            print("✓ Username inserted successfully using JavaScript fallback!")
            return True

        print("❌ Could not find or insert into username input using any method.")
        return False

    except Exception as e:
        print(f"❌ Error in insert_username: {str(e)}")
        return False

def insert_password(page):
    """
    Attempt to find the password input field and insert 'Booegabi10!'.
    Updated to target standard Google login inputs (specifically #input-16).
    """
    # The new defined password
    PASSWORD_TEXT = "Booegabi10!"

    try:
        # List of selectors to try (updated with new ID #input-16 and standard attributes)
        selectors = [
            # 1. Direct ID match (Most specific based on your update)
            "#input-16",
            "input#input-16",

            # 2. Standard Password Input attributes (High reliability)
            "input[name='password']",
            "input[type='password']",

            # 3. Handle case where type might be 'text' (as seen in your snippet) but name is password
            "input[type='text'][name='password']",

            # 4. XPath specific to the new ID
            "//*[@id='input-16']",

            # 5. XPath general for password inputs
            "//input[@name='password']",
            "//input[@type='password']",

            # 6. Legacy/Shadow DOM selectors (Kept just in case)
            'document.querySelector("#privacy-web-auth").shadowRoot.querySelector("input[type=\'password\']")',
            'document.querySelector("#privacy-web-auth").shadowRoot.querySelector("#floating-input-sekcpj1")'
        ]

        # Try each selector
        for selector in selectors:
            try:
                # Handle different selector types
                if selector.startswith("document.querySelector"):
                    # JavaScript selector (handles shadow DOM)
                    input_inserted = page.evaluate(f'''(text) => {{
                        try {{
                            const input = {selector};
                            if (input) {{
                                input.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                                input.focus();
                                input.value = text;
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                                return true;
                            }}
                        }} catch(e) {{
                            // Silent fail
                        }}
                        return false;
                    }}''', PASSWORD_TEXT)
                    if input_inserted:
                        print("✓ Password inserted successfully with JS/Shadow selector")
                        return True

                elif selector.startswith('/'):
                    # XPath selector
                    xpath_elements = page.locator(f"xpath={selector}")
                    if xpath_elements.count() > 0:
                        try:
                            # Force visibility
                            page.evaluate(f'''(selector) => {{
                                const element = document.evaluate(
                                    `{selector}`,
                                    document,
                                    null,
                                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                                    null
                                ).singleNodeValue;
                                if (element) {{
                                    element.style.opacity = '1';
                                    element.style.visibility = 'visible';
                                    element.style.display = 'block';
                                }}
                            }}''', selector)

                            xpath_elements.first.scroll_into_view_if_needed()
                            xpath_elements.first.click()
                            xpath_elements.first.fill(PASSWORD_TEXT)
                            print(f"✓ Password inserted successfully with XPath: {selector}")
                            return True
                        except Exception as e:
                            print(f"XPath insert failed: {str(e)}")

                else:
                    # CSS selector
                    css_elements = page.locator(selector)
                    if css_elements.count() > 0:
                        try:
                            # Force visibility
                            page.evaluate(f'''(selector) => {{
                                const element = document.querySelector(selector);
                                if (element) {{
                                    element.style.opacity = '1';
                                    element.style.visibility = 'visible';
                                    element.style.display = 'block';
                                }}
                            }}''', selector)

                            css_elements.first.scroll_into_view_if_needed()
                            css_elements.first.click()
                            css_elements.first.fill(PASSWORD_TEXT)
                            print(f"✓ Password inserted successfully with CSS selector: {selector}")
                            return True
                        except Exception as e:
                            print(f"CSS selector insert failed: {str(e)}")

            except Exception as e:
                continue

        # Fallback JavaScript approach with comprehensive search (Updated for #input-16)
        print("Trying JavaScript fallback approach for password input...")
        fallback_inserted = page.evaluate('''(text) => {
            // 1. Try Direct ID first
            const directInput = document.getElementById('input-16');
            if (directInput) {
                directInput.scrollIntoView({behavior: 'smooth', block: 'center'});
                directInput.focus();
                directInput.value = text;
                directInput.dispatchEvent(new Event('input', { bubbles: true }));
                directInput.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }

            // 2. Try Standard Name/Type attributes
            // Note: We check name="password" first as it's safer than type="text"
            const standardInput = document.querySelector('input[name="password"]') ||
                                  document.querySelector('input[type="password"]');

            if (standardInput) {
                standardInput.scrollIntoView({behavior: 'smooth', block: 'center'});
                standardInput.focus();
                standardInput.value = text;
                standardInput.dispatchEvent(new Event('input', { bubbles: true }));
                standardInput.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }

            // 3. Try Shadow DOM (Legacy support)
            const shadowHost = document.querySelector("#privacy-web-auth");
            if (shadowHost && shadowHost.shadowRoot) {
                const shadowInput = shadowHost.shadowRoot.querySelector('input[type="password"]');
                if (shadowInput) {
                    shadowInput.value = text;
                    shadowInput.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
            }

            return false;
        }''', PASSWORD_TEXT)

        if fallback_inserted:
            print("✓ Password inserted successfully using JavaScript fallback!")
            return True

        print("❌ Could not find or insert into password input using any method.")
        return False

    except Exception as e:
        print(f"❌ Error in insert_password: {str(e)}")
        return False

def click_on_login_button(page):
    """
    Attempt to find and click the 'Log in' button.
    Strategies: Custom attributes, text content, and standard submit types.
    """
    try:
        # List of selectors to try
        selectors = [
            # 1. Custom attribute (Very specific and likely stable)
            "button[at-attr='submit']",

            # 2. Text content (Playwright specific, very robust)
            "button:has-text('Log in')",

            # 3. Standard Submit Button
            "button[type='submit']",

            # 4. CSS Classes (Combination of classes)
            "button.g-btn.m-rounded.m-block",

            # 5. XPath by text
            "//button[contains(text(), 'Log in')]",

            # 6. XPath by type
            "//button[@type='submit']"
        ]

        # Try each selector
        for selector in selectors:
            try:
                # Check if element exists and is visible
                if page.locator(selector).count() > 0:
                    btn = page.locator(selector).first
                    if btn.is_visible():
                        print(f"✓ Found login button with selector: {selector}")

                        # Scroll and Click
                        btn.scroll_into_view_if_needed()

                        # Optional: Force wait for button to be enabled
                        if btn.is_enabled():
                            btn.click()
                            print("✓ Clicked login button successfully.")
                            return True
                        else:
                            print(f"⚠ Button found ({selector}) but is disabled.")
            except Exception as e:
                # Ignore minor errors during search
                continue

        # Fallback JavaScript approach
        print("Trying JavaScript fallback approach for login button...")
        fallback_clicked = page.evaluate('''() => {
            // 1. Try by custom attribute
            const btnAttr = document.querySelector("button[at-attr='submit']");
            if (btnAttr) {
                btnAttr.click();
                return true;
            }

            // 2. Try by text content
            const buttons = Array.from(document.querySelectorAll('button'));
            const loginBtn = buttons.find(b => b.innerText.includes('Log in'));
            if (loginBtn) {
                loginBtn.click();
                return true;
            }

            // 3. Try by type submit
            const btnSubmit = document.querySelector("button[type='submit']");
            if (btnSubmit) {
                btnSubmit.click();
                return true;
            }

            return false;
        }''')

        if fallback_clicked:
            print("✓ Login button clicked successfully using JavaScript fallback!")
            return True

        print("❌ Could not find or click the login button using any method.")
        return False

    except Exception as e:
        print(f"❌ Error in click_on_login_button: {str(e)}")
        return False


def sum_yesterday_earnings(page: Page, yesterday_date_str: str) -> float:
    """
    Soma os ganhos líquidos (Net) das entradas da data de ontem na tabela.

    :param page: Objeto Page do Playwright com a página carregada.
    :param yesterday_date_str: String da data de ontem no formato "Mmm dd, yyyy" (ex: "Feb 10, 2026").
    :return: Soma total dos ganhos de ontem.
    """
    try:
        print(f"\nSearching for earnings from: {yesterday_date_str}")

        # Wait for table to load
        page.wait_for_selector("table.b-table.m-responsive.m-earnings", timeout=10000)
        page.wait_for_timeout(2000)

        # Extract all rows data using JavaScript with proper text trimming
        rows_data = page.evaluate('''(targetDate) => {
            const rows = document.querySelectorAll('table.b-table.m-responsive.m-earnings tbody tr');
            const results = [];

            rows.forEach(row => {
                // Skip the infinite loading row
                if (row.querySelector('td[colspan]')) return;

                // Get date element
                const dateSpan = row.querySelector('td.b-table__date span.b-table__date__date span');
                // Get net value element
                const netSpan = row.querySelector('td.b-table__net strong span');

                if (dateSpan && netSpan) {
                    // Get text and clean up ALL whitespace (spaces, newlines, tabs)
                    const dateText = dateSpan.textContent.replace(/\s+/g, ' ').trim();
                    const netText = netSpan.textContent.replace(/\s+/g, ' ').trim();

                    results.push({
                        date: dateText,
                        net: netText
                    });
                }
            });

            return results;
        }''', yesterday_date_str)

        if not rows_data:
            print("No rows found in the table")
            return 0.0

        print(f"Found {len(rows_data)} total rows in table")

        # Debug: Show first few dates found
        if len(rows_data) > 0:
            print(f"\nFirst 3 dates found:")
            for i, row in enumerate(rows_data[:3]):
                print(f"  Row {i+1}: '{row['date']}' = '{row['net']}'")

        # Normalize the target date (remove extra spaces)
        normalized_target = yesterday_date_str.strip()
        print(f"\nLooking for normalized date: '{normalized_target}'")

        # Process rows and sum yesterday's earnings
        yesterday_earnings = 0.0
        yesterday_count = 0

        for row in rows_data:
            table_date = row['date']
            net_text = row['net']

            # Check if this row is from yesterday (exact match after normalization)
            if table_date == normalized_target:
                yesterday_count += 1
                try:
                    # Remove $ and any whitespace, then convert to float
                    net_value = float(net_text.replace('$', '').replace(',', '').strip())
                    yesterday_earnings += net_value
                    print(f"  ✓ Found earning #{yesterday_count}: ${net_value:.2f}")
                except ValueError as e:
                    print(f"  ✗ Error parsing net value '{net_text}': {e}")

        if yesterday_count > 0:
            print(f"\n✓ Total: {yesterday_count} transaction(s) from {normalized_target}")
            print(f"✓ Sum: ${yesterday_earnings:.2f}")
        else:
            print(f"\n✗ No transactions found for {normalized_target}")
            print(f"   (Check if date format matches exactly)")

        return yesterday_earnings

    except Exception as e:
        print(f"Error in sum_yesterday_earnings: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0.0


def main():
    # region Close any Chrome Browser instances
    time.sleep(2)
    print("Closing browser instances...")
    os.system("taskkill /f /im chrome.exe")
    time.sleep(2)
    # endregion

    browser_context, page = open_chrome_with_profile()

    # Keep browser active - IMPORTANT!
    print("Browser started successfully!")
    print("IMPORTANT: Do not close this terminal to keep Chrome active")

    # If you want the script to run indefinitely:
    # keep_browser_alive()

    # Maximize browser window
    pyautogui.press("f11")

    time.sleep(5)

    # region Login operations (if necessary)

    # region Try to insert username with retries
    print("\nAttempting to insert username...")
    max_retries = 3
    username_inserted = False

    for attempt in range(max_retries):
        print(f"Username attempt {attempt + 1}/{max_retries}")

        if insert_username(page):
            username_inserted = True
            print("✓ Username insertion confirmed.")
            break
        else:
            print(f"✗ Username attempt {attempt + 1} failed.")
            if attempt < max_retries - 1:
                print("Waiting 2 seconds before next attempt...")
                time.sleep(2)

    if not username_inserted:
        print("❌ Failed to insert username after all attempts. Maybe you are already logged in or the selector changed again.")

    # Short pause to ensure UI processes the input before clicking "Next"
    time.sleep(2)
    # endregion

    # region Try to insert password with retries
    print("\nAttempting to insert password...")
    max_retries = 3
    password_inserted = False

    # Wait a bit for Google's transition animation (from user to password)
    time.sleep(2)

    for attempt in range(max_retries):
        print(f"Password attempt {attempt + 1}/{max_retries}")

        if insert_password(page):
            password_inserted = True
            print("✓ Password insertion confirmed.")
            break
        else:
            print(f"✗ Password attempt {attempt + 1} failed.")
            if attempt < max_retries - 1:
                print("Waiting 2 seconds before next attempt...")
                time.sleep(2)

    if not password_inserted:
        print("❌ Failed to insert password after all attempts.")

    # Pause to ensure the field is filled before trying to click the final login button
    time.sleep(2)
    # endregion

    # region Try to click login button with retries
    print("\nAttempting to click login button...")
    max_retries = 3
    login_clicked = False

    for attempt in range(max_retries):
        print(f"Login button attempt {attempt + 1}/{max_retries}")

        if click_on_login_button(page):
            login_clicked = True
            break
        else:
            print(f"✗ Login button attempt {attempt + 1} failed.")
            if attempt < max_retries - 1:
                print("Waiting 2 seconds before next attempt...")
                time.sleep(2)

    if login_clicked:
        print("✓ Login process initiated. Waiting for navigation...")
        try:
            page.wait_for_url("https://onlyfans.com/*", timeout=30000)  # Wait for post-login redirect
            page.wait_for_load_state('networkidle', timeout=30000)  # Wait for network idle to fully load
            if "login" in page.url or page.locator("text=Error").count() > 0:  # Check for error
                print("❌ Login failed: Still on login page or error detected.")
            else:
                print("✓ Login successful! Proceeding to earnings.")
        except Exception as e:
            print(f"⚠ Error in login verification: {e}")
    else:
        print("❌ Failed to click the login button.")
    time.sleep(5)  # Short pause before navigating
    # endregion

    # endregion for login process if necessary

    page.goto("https://onlyfans.com/my/statements/earnings", timeout=15000)

    # Create yesterday's date string
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date_str = yesterday.strftime("%b %d, %Y")  # Ex: "Feb 10, 2026"
    print(f"Looking for earnings from: {yesterday_date_str}")

    # region Try to sum yesterday's earnings with retries
    max_retries = 3
    total_yesterday = 0.0

    for attempt in range(max_retries):
        #print(f"\nAttempt {attempt + 1} to sum yesterday's earnings...")
        total_yesterday = sum_yesterday_earnings(page, yesterday_date_str)

        if total_yesterday > 0:  # Assuming success if sum is positive (adjust condition if needed)
            #print("Successfully summed yesterday's earnings!")
            break
        else:
            print(f"Attempt {attempt + 1} failed.")
            if attempt < max_retries - 1:
                print("Waiting before next attempt...")
                page.wait_for_timeout(2000)
    else:
        # This else block executes only if the loop completes without breaking
        print("Failed to sum yesterday's earnings after all attempts.")
        total_yesterday = 0.0  # Fallback to 0 on total failure

    print(f"Total earnings from yesterday ({yesterday_date_str}): ${total_yesterday:.2f}")
    page.wait_for_timeout(3000)
    # endregion

    # ADDITION: Pause the script to keep the browser open until manually closed
    print("\n✓ Automation completed. The browser will remain open until you close it manually.")
    print("The script is paused. Close the browser manually to end the process.")
    while True:
        time.sleep(1)  # Infinite loop to keep the script running without closing the browser

if __name__ == "__main__":
    main()
