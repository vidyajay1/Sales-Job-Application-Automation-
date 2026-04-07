from playwright.sync_api import sync_playwright

FORM_URL = "https://airtable.com/appiPekJv9PdMSORq/pagHDDxQnMHRJxILZ/form"

START_CODE = 3156
END_CODE = 3561

FORM_DATA = {
    "name": "Vidya Jayaraman",
    "email": "viamorgloss@gmail.com",
    "whatsapp": "+18583442710",
    "one_liner": "I have experience in full-cycle sales, scaling accounts from 10 to 150+ and generating $60K+ in commissions in the sales team I managed.",
    "source": "Paid in Full",
}


def fill_field_smart(page, label_text, value):
    try:
        page.get_by_label(label_text, exact=False).fill(str(value))
        return
    except:
        pass

    try:
        container = page.locator(f"text={label_text}").locator("..")
        input_box = container.locator("input, textarea").first
        input_box.fill(str(value))
        return
    except:
        pass

    print(f"⚠️ Could not find field: {label_text}")


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
    page.wait_for_timeout(3000)

    fill_field_smart(page, "Name", FORM_DATA["name"])
    fill_field_smart(page, "Email Address", FORM_DATA["email"])
    fill_field_smart(page, "WhatsApp Phone Number", FORM_DATA["whatsapp"])
    fill_field_smart(page, "One Liner", FORM_DATA["one_liner"])
    fill_field_smart(page, "Where did you find this application", FORM_DATA["source"])

    formatted_code = fill_job_code(page, code)

    # ✅ AUTO SUBMIT
    page.get_by_role("button", name="Submit").click()

    # wait for confirmation / reset
    page.wait_for_timeout(3000)

    print(f"✅ Submitted {formatted_code}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        for code in range(START_CODE, END_CODE + 1):
            try:
                apply_once(page, code)
            except Exception as e:
                print(f"❌ Error on {code:05d}: {e}")

        browser.close()


if __name__ == "__main__":
    main()