from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import re
import smtplib
from email.mime.text import MIMEText

FORM_URL = "https://airtable.com/appiPekJv9PdMSORq/pagHDDxQnMHRJxILZ/form"
PAIDINFULL_LOGIN_URL = "https://paidinfull.vip/login"
GMAIL_USER = "jayaramanvidya1@gmail.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
START_CODE = 3606
END_CODE = 3701
PAIDINFULL_USER = os.getenv("PAIDINFULL_USER")
PAIDINFULL_PASS = os.getenv("PAIDINFULL_PASS")

FORM_DATA = {
    "name": "xxxx",
    "email": "xxxx",
    "whatsapp": "+xxxx0",
    "one_liner": "xxxx.",
    "source": "xxxx",
}


def fill_field_smart(page, label_text, value):
    try:
        page.get_by_label(label_text, exact=False).fill(str(value))
        return True
    except:
        pass

    try:
        container = page.locator(f"text={label_text}").locator("..")
        input_box = container.locator("input, textarea").first
        input_box.fill(str(value))
        return True
    except:
        pass

    print(f"⚠️ Could not find field: {label_text}")
    return False


def fill_job_code(page, code):
    formatted_code = f"{code:05d}"

    try:
        page.get_by_label("JOB CODE", exact=False).fill(formatted_code)
        return formatted_code
    except:
        pass

    try:
        container = page.locator("text=JOB CODE").locator("..")
        input_box = container.locator("input").first
        input_box.fill(formatted_code)
        return formatted_code
    except:
        pass

    print("⚠️ JOB CODE field not found")
    return formatted_code


def apply_once(page, code):
    page.goto(FORM_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    fill_field_smart(page, "Name", FORM_DATA["name"])
    fill_field_smart(page, "Email Address", FORM_DATA["email"])
    fill_field_smart(page, "WhatsApp Phone Number", FORM_DATA["whatsapp"])
    fill_field_smart(page, "One Liner", FORM_DATA["one_liner"])
    fill_field_smart(page, "Where did you find this application", FORM_DATA["source"])

    formatted_code = fill_job_code(page, code)

    page.get_by_role("button", name="Submit").click()
    page.wait_for_timeout(3000)

    print(f"✅ Submitted {formatted_code}")


def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip().lower()


def should_apply(description_text):
    """
    Apply only if setter is present.
    Skip if it only mentions closer / closing and no setter indicators.
    """
    text = normalize_text(description_text)

    setter_keywords = [
        "setter",
        "appointment setter",
        "setting appointments",
        "book appointments",
        "booking calls",
        "lead qualification",
        "qualify leads",
        "inbound setter",
        "outbound setter",
        "setter / closer",
        "setter-closer",
        "sales setter",
    ]

    closer_keywords = [
        "closer",
        "closing calls",
        "close deals",
        "high ticket closer",
        "sales closer",
    ]

    has_setter = any(k in text for k in setter_keywords)
    has_closer = any(k in text for k in closer_keywords)

    # Apply when setter is explicitly mentioned, even if setter/closer hybrid
    if has_setter:
        return True

    # If it only looks like closer language, skip
    if has_closer and not has_setter:
        return False

    # Conservative default: skip if setter is not found
    return False


def login_paidinfull(page):
    if not PAIDINFULL_USER or not PAIDINFULL_PASS:
        raise RuntimeError(
            "Missing credentials. Set PAIDINFULL_USER and PAIDINFULL_PASS as environment variables."
        )

    page.goto(PAIDINFULL_LOGIN_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    print(f"Page title: {page.title()}")
    print(f"Current URL: {page.url}")
    
    # Print all inputs found
    print("\nAvailable inputs on page:")
    inputs = page.locator("input").all()
    for i, inp in enumerate(inputs):
        print(f"  Input {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}")

    # Try to fill each input field directly
    email_filled = False
    password_filled = False

    for i, inp in enumerate(inputs):
        input_type = inp.get_attribute('type')
        input_name = inp.get_attribute('name')
        
        if input_type == 'email' or 'email' in str(input_name).lower():
            try:
                inp.clear()
                inp.type(PAIDINFULL_USER, delay=50)
                print(f"✅ Filled email into input {i}")
                email_filled = True
            except Exception as e:
                print(f"❌ Failed to fill email: {e}")
        
        elif input_type == 'password' or 'password' in str(input_name).lower():
            try:
                inp.clear()
                inp.type(PAIDINFULL_PASS, delay=50)
                print(f"✅ Filled password into input {i}")
                password_filled = True
            except Exception as e:
                print(f"❌ Failed to fill password: {e}")

    if not email_filled or not password_filled:
        raise RuntimeError("Could not fill login credentials")

    # Click submit button
    buttons = page.locator("button").all()
    for btn in buttons:
        btn_text = btn.inner_text().lower()
        if any(x in btn_text for x in ['login', 'sign in', 'submit', 'continue']):
            try:
                btn.click()
                print("✅ Clicked login button")
                break
            except Exception as e:
                print(f"Failed to click button: {e}")

    page.wait_for_timeout(5000)
    print("✅ Logged into paidinfull.vip")
# ...existing code...


def find_and_open_job(page, code):
    formatted_code = f"{code:05d}"

    # Try search input first
    search_selectors = [
        'input[type="search"]',
        'input[placeholder*="search" i]',
        'input[name*="search" i]',
    ]

    searched = False
    for selector in search_selectors:
        try:
            search = page.locator(selector).first
            search.fill("")
            search.fill(formatted_code)
            search.press("Enter")
            page.wait_for_timeout(2500)
            searched = True
            break
        except:
            continue

    # If no search box, try navigating directly to a likely URL pattern
    if not searched:
        candidate_urls = [
            f"https://paidinfull.vip/jobs/{formatted_code}",
            f"https://paidinfull.vip/job/{formatted_code}",
            f"https://paidinfull.vip/opportunities/{formatted_code}",
        ]
        for url in candidate_urls:
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                if formatted_code in page.content():
                    return True
            except:
                continue

    # Try clicking a result/card that contains the job code
    click_patterns = [
        page.get_by_text(formatted_code, exact=False),
        page.locator(f"text={formatted_code}"),
    ]

    for locator in click_patterns:
        try:
            locator.first.click()
            page.wait_for_timeout(2500)
            return True
        except:
            continue

    # Maybe the search itself loaded the details on the same page
    return formatted_code in page.content()


def extract_job_description(page, code):
    formatted_code = f"{code:05d}"

    # Best-effort extraction from likely containers
    candidate_selectors = [
        "main",
        "article",
        '[class*="job"]',
        '[class*="description"]',
        '[class*="content"]',
        '[class*="details"]',
        "body",
    ]

    texts = []
    for selector in candidate_selectors:
        try:
            text = page.locator(selector).first.inner_text(timeout=2000)
            if text and formatted_code in text or len(text) > 200:
                texts.append(text)
        except:
            continue

    if texts:
        # Return the longest text block
        return max(texts, key=len)

    return page.content()

def send_email(job_code, job_title, status):
    print("\n" + "="*60)
    print(f"📌 JOB UPDATE")
    print(f"Code   : {job_code:05d}")
    print(f"Title  : {job_title}")
    print(f"Status : {status}")
    print("="*60 + "\n")

def extract_job_title(page):
    candidate_selectors = [
        "h1",
        "h2",
        '[class*="job-title"]',
        '[class*="position"]',
        '[class*="title"]',
    ]

    for selector in candidate_selectors:
        try:
            elements = page.locator(selector).all()
            for elem in elements:
                title = elem.inner_text(timeout=2000).strip()
                # Skip generic titles
                if title and title not in ["Find Jobs", "Home", "Login", "Search"]:
                    return title
        except:
            continue

    return "Unknown Title"
def process_job_code(page, code):
    formatted_code = f"{code:05d}"
    print(f"\n🔎 Checking {formatted_code}")

    found = find_and_open_job(page, code)
    if not found:
        print(f"⚠️ Could not locate job {formatted_code}")
        return

    description = extract_job_description(page, code)
    title = extract_job_title(page)

    if should_apply(description):
        status = "APPLYING"
        print(f"✅ Setter match found for {formatted_code}")
        
        # ✅ Send email BEFORE applying
        send_email(code, title, status)

        apply_once(page, code)
    else:
        status = "SKIPPED"
        print(f"⏭️ Skipping {formatted_code} — closer-only or no setter")

        # ✅ Send email even if skipped
        send_email(code, title, status)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        context = browser.new_context()
        page = context.new_page()

        try:
            login_paidinfull(page)

            for code in range(START_CODE, END_CODE + 1):
                try:
                    # Return to site home or jobs page before each lookup if needed
                    page.goto(PAIDINFULL_LOGIN_URL, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                    process_job_code(page, code)
                except Exception as e:
                    print(f"❌ Error on {code:05d}: {e}")

        finally:
            browser.close()


if __name__ == "__main__":
    main()