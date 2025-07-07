# email_flagging_using_Langchain
# 📧 Email Flagging System

An automated email flagging system that scans a Gmail inbox for potentially suspicious emails using the Gmail API and OpenAI's GPT-4. It identifies phishing or malicious messages, moves them to a custom Gmail label, stores results locally, and provides a user-friendly web interface using Streamlit.

---

## 🚀 Features

- **🔐 Gmail Integration**: Authenticates and accesses your Gmail inbox using the Gmail API.
- **🤖 AI-Powered Detection**: Uses GPT-4 to analyze email content for phishing/red flags (urgent tones, suspicious links, mismatched domains).
- **🏷 Gmail Labeling**: Flags and moves suspicious emails to a `Flagged_Suspicious` label.
- **💾 Local Storage**: Saves flagged email details as `.txt` files in `flagged_emails/`.
- **🌐 Streamlit Interface**: Web UI to scan emails, configure scan limits, and display flagged results.
- **📋 Logging**: Logs errors and processing steps to `email_processing.log`.

---

## 📦 Prerequisites

- Python 3.8 or higher
- Gmail account with API access
- OpenAI API key (GPT-4)
- Google Cloud project with Gmail API enabled
- `credentials.json` file from Google Cloud Console *(not included)*

---

## 🔐 Security Notice

**DO NOT COMMIT THE FOLLOWING FILES:**

- `.env`: Contains `OPENAI_API_KEY` and Gmail address
- `credentials.json`: Google OAuth credentials
- `token.json`: Gmail access/refresh token
- `email_processing.log`: Runtime log data
- `flagged_emails/`: Contains flagged email data

> ⚠️ If any sensitive file was committed accidentally:
> - **Revoke the credentials** from Google Cloud
> - **Generate new API keys**
> - **Rotate your OpenAI API key immediately**

---

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/email-flagging-system.git
cd email-flagging-system
