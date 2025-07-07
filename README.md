# email_flagging_using_Langchain
Email Flagging System

This project is an automated email flagging system that scans a Gmail inbox for potentially suspicious emails using the Gmail API and OpenAI's GPT-4 model. It identifies phishing or malicious emails, moves them to a "Flagged_Suspicious" label in Gmail, saves details to local text files in a flagged_emails folder, and displays results in a user-friendly Streamlit web interface.

Features





Gmail Integration: Authenticates with the Gmail API to fetch emails from the inbox.



Suspicious Email Detection: Uses GPT-4 to analyze email content for phishing indicators (e.g., urgent requests, suspicious links, mismatched domains).



Gmail Labeling: Moves flagged emails to a "Flagged_Suspicious" label in Gmail for easy identification.



Local Storage: Saves details of flagged emails to text files in a local flagged_emails folder.



Streamlit Interface: Provides a web-based UI to configure the number of emails to scan (1–50) and view results with expandable sections.



Logging: Records processing details and errors in email_processing.log for debugging and auditing.

Prerequisites





Python: Version 3.8 or higher.



Gmail Account: With API access enabled.



OpenAI API Key: For GPT-4 email analysis.



Google Cloud Project: With the Gmail API enabled and credentials.json downloaded (not included in the repository).

Security Notice

Critical: Do not commit sensitive files to GitHub or any public repository. The following files contain sensitive information and are excluded from version control via .gitignore:





.env: Contains OPENAI_API_KEY and EMAIL_USER.



credentials.json: Contains Gmail API credentials (client_id, client_secret).



token.json: Contains authentication tokens (generated during runtime).



email_processing.log: Contains log data with potential sensitive information.



flagged_emails/: Contains output files with email details.

Action: Ensure these files are never added to Git. If accidentally committed, immediately remove them from the repository history using git rm --cached <file> and regenerate credentials or API keys if exposed.

Installation





Clone the Repository:

git clone https://github.com/your-username/email-flagging-system.git
cd email-flagging-system



Install Dependencies:

pip install -r requirements.txt

If requirements.txt is not provided, install the following packages:

pip install streamlit langchain-openai google-auth-oauthlib google-api-python-client beautifulsoup4 python-dotenv



Set Up Environment Variables: Create a .env file in the project root with the following content:

OPENAI_API_KEY="your_openai_api_key"
EMAIL_USER="your_gmail_address"

Ensure .env is not committed to GitHub (it’s included in .gitignore).



Configure Gmail API:





Visit the Google Cloud Console.



Create a project and enable the Gmail API.



Create OAuth 2.0 credentials and download the credentials.json file.



Place credentials.json in the project root (do not commit to GitHub).



Ensure the credentials include the scope: https://www.googleapis.com/auth/gmail.modify.



Verify .gitignore: Ensure the .gitignore file in the project root contains:

.env
credentials.json
token.json
email_processing.log
flagged_emails/

This prevents sensitive files from being committed to GitHub.

Usage





Run the Streamlit App:

streamlit run email_agents.py

This starts a local server, typically at http://localhost:8501.



Authenticate with Gmail:





On first run, a browser window will open for Gmail authentication.



Follow the prompts to authorize the application.



A token.json file will be created in the project root to store authentication details (not committed to GitHub).



Use the Streamlit Interface:





Open the provided URL (e.g., http://localhost:8501) in your browser.



In the interface, specify the number of emails to scan (1–50, default is 5).



Click the "Scan Emails" button to start processing.



View results in expandable sections showing flagged emails with details (subject, sender, date, risk assessment, local file location).



Check the "Flagged_Suspicious" label in your Gmail account for flagged emails.



Check the flagged_emails folder in the project root for text files containing details of flagged emails.

File Structure

email-flagging-system/
│
├── email_agents.py         # Main script with email processing and Streamlit UI
├── .gitignore             # Excludes sensitive files from version control
├── .env                   # Environment variables (not in version control)
├── credentials.json       # Gmail API credentials (not in version control)
├── token.json             # Gmail API authentication token (generated, not in version control)
├── email_processing.log   # Log file for processing details and errors (not in version control)
├── flagged_emails/        # Folder containing text files of flagged emails (not in version control)
└── README.md              # Project documentation

Example Output





Streamlit Interface:





Displays flagged emails in expandable sections with details (subject, sender, date, risk assessment, local file location).



Shows debug information (working directory, files, email user) in an expandable section.



Includes a progress bar during email processing.



Gmail:





Flagged emails are moved to the "Flagged_Suspicious" label in your Gmail account.



Local Files:





Text files in the flagged_emails/ folder, named like flagged_email_YYYYMMDD_HHMMSS_messageid.txt, containing email details and risk assessment.

Troubleshooting





Authentication Errors:





Verify that credentials.json is valid and includes the https://www.googleapis.com/auth/gmail.modify scope.



Delete token.json and re-run the script to force re-authentication.



API Key Issues:





Ensure the OPENAI_API_KEY in .env is valid and correctly formatted.



Streamlit Errors:





Run the script with streamlit run email_agents.py, not python email_agents.py.



If you see "missing ScriptRunContext" warnings, ensure you’re using the correct command.



No Emails Flagged:





Check if your inbox has emails or increase the email_limit in the Streamlit interface.



Review email_processing.log for detailed error messages.



Sensitive Files Committed:





If credentials.json, .env, or token.json were accidentally committed, remove them using:

git rm --cached <file>
git commit -m "Remove sensitive file from version control"
git push origin main



Regenerate credentials in the Google Cloud Console and update credentials.json.

Contributing

Contributions are welcome! To contribute:





Fork the repository.



Create a feature branch (git checkout -b feature/your-feature).



Commit your changes (git commit -m "Add your feature").



Push to the branch (git push origin feature/your-feature).



Open a pull request.

Please ensure sensitive files are not included in your commits.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments





Built with Streamlit, LangChain, and Google API Client.



Uses OpenAI's GPT-4 for email content analysis.



Inspired by the need for automated phishing detection in email systems.

Contact

For questions or issues, please open an issue on the GitHub repository or contact the maintainer at [your-email@example.com].
