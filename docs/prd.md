Perfect — you’ve structured the PRD very well 👏
Let’s enhance it according to your new Excel schema and logic.

Below is the **updated, production-ready PRD** that now supports:
✅ Excel columns: `Business Name`, `Description`, `Website`, `Phone`, `Google Maps Link`
✅ Logic for *adaptive message selection* —
→ if a business **already has a website**, the bot sends a **“website enhancement / redesign”** message,
→ otherwise, it sends a **“website creation offer”** message.

---

# Product Requirements Document (PRD) — WhatsApp Cold-Message Automation (Selenium)

**Project name:** WA-Website-Offer-Automation
**Author:** (you)
**Date:** 2025-10-16
**Audience:** Product owner, developer(s), QA, legal/compliance

---

## 1. Summary / Purpose

Build a reliable, safe, and maintainable WhatsApp Web automation using Selenium that reads a list of businesses and phone numbers from an Excel file and sends persuasive cold messages offering **either website creation** or **website enhancement** services based on whether the business already has a website.

The system must minimize the need to re-scan the WhatsApp QR code — i.e., the user logs in once and subsequent runs reuse the same authenticated session. Implement anti-ban measures (random delays, message variation, and rate limiting) and logging/monitoring.

---

## 2. Goals & Success Metrics

**Goals**

* Automate personalized WhatsApp messaging using data from Excel.
* Detect whether a business already has a website and adapt the message accordingly.
* Maintain a persistent WhatsApp Web session (QR scanned once).
* Prevent WhatsApp account bans with rate limiting and randomized delays.
* Provide structured logs and retry/error handling.

**Success Metrics**

* ≥ 95% successful message delivery for valid numbers.
* ≥ 95% reuse of session without re-scanning QR.
* 0 banned accounts in 30-day pilot (with safe rate limits).
* 100% of messages correctly chosen between *“create”* and *“enhance”* templates based on website availability.

---

## 3. Features (High-level)

1. Import contacts from Excel (`Business Name`, `Description`, `Website`, `Phone`, `Google Maps Link`).
2. Detect website presence:

   * If `Website` cell is empty → use *Website Creation Offer Template*.
   * If `Website` cell contains a URL → use *Website Enhancement / Redesign Template*.
3. Compose personalized messages with placeholders (`{business_name}`, `{description}`, `{website}`).
4. Use persistent Chrome profile for WhatsApp Web login (no re-scan).
5. Apply random message delays to avoid spam detection.
6. Log delivery status (success, failure, error).
7. Retry transient failures with backoff.
8. Include dry-run mode for QA.
9. Configurable rate limiting and batch delay.
10. Export logs to CSV.

---

## 4. Functional Requirements (Detailed)

### 4.1 Input

System reads an Excel file `data.xlsx` with these columns:

| Column           | Type   | Description                                                     |
| ---------------- | ------ | --------------------------------------------------------------- |
| Business Name    | string | Name of the business                                            |
| Description      | string | Short description (optional)                                    |
| Website          | string | Business website URL (if any)                                   |
| Phone            | string | WhatsApp number in international format (e.g., `6281234567890`) |
| Google Maps Link | string | Link to the business on Google Maps (optional)                  |

---

### 4.2 Message Composition

* Use multiple message templates.
* Tokens: `{business_name}`, `{description}`, `{website}`.
* Two main template groups:

  1. **Creation Offer Templates** — for businesses without a website.
  2. **Enhancement Offer Templates** — for businesses with an existing website.
* Add randomized emoji and word variations.

---

### 4.3 Sending Logic

For each valid row in the Excel file:

1. Read `Website` field.
2. Choose the appropriate template group.
3. Generate message and URL-encode it.
4. Open `https://web.whatsapp.com/send?phone={phone}&text={message}`.
5. Wait until chat loads.
6. Click the Send button.
7. Record status (success/error).
8. Wait for a random delay before the next message.

---

### 4.4 Session Persistence (No QR on Each Run)

* Use a persistent Chrome profile with:

  ```bash
  --user-data-dir=chrome_profile_whatsapp
  --profile-directory=Default
  ```
* On first run, scan QR code.
* Subsequent runs automatically reuse the same authenticated session.
* Protect the `chrome_profile_whatsapp` directory (contains session tokens).

---

### 4.5 Anti-Ban & Throttling

* Delay between messages: 20–90 seconds (randomized).
* After 10–20 messages, add a long rest (5–15 minutes).
* Max 50 messages/day per account.
* Rotate templates and vary emojis.
* Skip numbers with invalid format or empty `Phone`.

---

### 4.6 Logging & Monitoring

* Log to CSV with:

  ```
  timestamp, business_name, phone, website, message_type, status, error
  ```
* Console summary of sent/failed counts.
* Optional JSON logging for advanced analytics.

---

### 4.7 Error Handling & Retries

* Retry up to 3 times for network/UI errors with exponential backoff.
* Skip permanently invalid numbers.
* Log all failures.

---

### 4.8 Dry-Run Mode

* Preview messages (printed to console) without sending.
* Confirms correct template selection and personalization.

---

## 5. Message Templates (English)

### **A. For Businesses Without a Website (Website Creation Offer)**

**Template A1 — Short & Direct**
Hi {business_name}, your business sounds amazing! I help local brands like yours create professional websites that attract more customers online. Would you like me to send a free mockup idea?

**Template A2 — Value-Driven**
Hello {business_name}, I came across your business — it looks great! I specialize in creating simple, beautiful websites that make it easier for customers to find and contact you. Want to see a free demo?

**Template A3 — Social Proof**
Hi {business_name}, we recently helped a similar business increase online leads by 40% after launching a modern website. I’d love to show you how a site could boost your visibility too. Shall I send you an example?

---

### **B. For Businesses That Already Have a Website (Website Enhancement Offer)**

**Template B1 — Modern Upgrade Pitch**
Hey {business_name}, I checked out your website ({website}) — it’s great! I specialize in modern redesigns that improve speed, mobile look, and Google ranking. Would you like a free concept preview?

**Template B2 — Performance Focus**
Hello {business_name}, I saw your website and think it could attract even more customers with a cleaner layout and better mobile performance. I can prepare a few enhancement ideas at no cost — interested?

**Template B3 — Professional Appeal**
Hi {business_name}, your current site looks good, but a refreshed design could make it feel more premium and boost conversions. I can share a quick concept for free if you’re open to it!

---

## 6. Rate Limiting & Delay Strategy

| Type              | Range                         | Purpose                     |
| ----------------- | ----------------------------- | --------------------------- |
| Per-message delay | 20–90 sec                     | Avoid detection             |
| Per-batch delay   | 5–15 min after 10–20 messages | Natural pacing              |
| Max/day           | 30–50                         | Conservative anti-ban limit |

---

## 7. Implementation Notes (Code Highlights)

### Detecting Template Type

```python
if pd.isna(row['Website']) or row['Website'].strip() == "":
    message_template = random.choice(creation_templates)
    message_type = "creation"
else:
    message_template = random.choice(enhancement_templates)
    message_type = "enhancement"
```

### Persistent Chrome Session

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

profile_path = os.path.abspath("chrome_profile_whatsapp")
os.makedirs(profile_path, exist_ok=True)

options = Options()
options.add_argument(f"--user-data-dir={profile_path}")
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")
```

---

## 8. UX / Operator Flow

1. Prepare `data.xlsx` with all columns.
2. Run the script (first time → scan QR).
3. Choose mode: `--dry-run` or `--send`.
4. Observe logs and status output.
5. Subsequent runs reuse session automatically.

---

## 9. Testing Plan

* Run small test (5–10 contacts) with both “Website” and “No Website” rows.
* Verify correct message templates chosen.
* Check message delivery and logs.
* Monitor WhatsApp activity for warnings.

---

## 10. Risks & Mitigations

| Risk                       | Mitigation                                     |
| -------------------------- | ---------------------------------------------- |
| Account banned             | Random delays, varied templates, low volume    |
| UI change breaks selectors | Use configurable XPaths and fallback detection |
| QR re-login needed         | Reuse Chrome profile                           |
| Legal issues               | Add opt-out and follow regional regulations    |
| Privacy                    | Restrict access to WhatsApp profile directory  |

---

## ✅ Outcome

When fully implemented, this automation will:

* Intelligently detect businesses that already have a website.
* Send personalized, non-spammy marketing messages that fit their current digital stage.
* Operate safely through session reuse, randomized delays, and ethical throttling.
* Log all activity transparently for review.

---

Would you like me to now generate the **Python script** that fully implements this updated PRD (including both “creation” and “enhancement” message logic, logging, and persistent session)?
