

import os
import base64
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import logging
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

gpt4 = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

class EmailFlaggingSystem:
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.flagged_folder = "Flagged_Suspicious"
        self.local_output_dir = "flagged_emails"
        try:
            self.service = self._get_gmail_service()
            self._create_label_if_not_exists()
            self._create_local_output_dir()
            st.success("Gmail API authentication successful")
        except Exception as e:
            st.error(f"Failed to initialize Gmail service: {str(e)}")
            logger.error(f"Initialization failed: {str(e)}")
            raise

    def _get_gmail_service(self):
        """Authenticate and create Gmail API service"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        creds = None
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token.json')
        credentials_path = os.path.join(current_dir, 'credentials.json')
        
        st.write(f"Looking for credentials at: {credentials_path}")
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}\n"
                    "Please download it from Google Cloud Console and place in this folder"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)

    def _create_label_if_not_exists(self):
        """Create Flagged_Suspicious label if it doesn't exist"""
        try:
            labels = self.service.users().labels().list(userId='me').execute().get('labels', [])
            for label in labels:
                if label['name'].lower() == self.flagged_folder.lower():
                    self.flagged_label_id = label['id']
                    return
            
            label = {
                'name': self.flagged_folder,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(userId='me', body=label).execute()
            self.flagged_label_id = created_label['id']
            logger.info(f"Created new Gmail label: {self.flagged_folder}")
        except Exception as e:
            logger.error(f"Failed to create/check label: {str(e)}")
            raise

    def _create_local_output_dir(self):
        """Create local directory for flagged emails"""
        if not os.path.exists(self.local_output_dir):
            os.makedirs(self.local_output_dir)
            logger.info(f"Created local output directory: {self.local_output_dir}")

    def _save_flagged_email_locally(self, email, risk_score, msg_id):
        """Save flagged email details to a local text file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.local_output_dir}/flagged_email_{timestamp}_{msg_id}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"From: {email['sender']}\n")
                f.write(f"Date: {email['date']}\n")
                f.write(f"Message ID: {msg_id}\n")
                f.write(f"\nRisk Assessment:\n{risk_score}\n")
                f.write(f"\nEmail Body (truncated):\n{email['body'][:1000]}...")
            logger.info(f"Saved flagged email to: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save flagged email locally: {str(e)}")
            return None

    def fetch_emails(self, folder="INBOX", limit=10):
        """Fetch emails using Gmail API"""
        try:
            label_id = self._get_label_id(folder)
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id],
                maxResults=limit
            ).execute()
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._parse_email(msg['id'])
                if email_data:
                    email_data['msg_id'] = msg['id']
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            st.error(f"GMAIL API ERROR: {str(e)}")
            logger.error(f"Gmail API error: {str(e)}")
            return []

    def _get_label_id(self, folder_name):
        """Convert folder name to Gmail label ID"""
        labels = self.service.users().labels().list(userId='me').execute().get('labels', [])
        for label in labels:
            if label['name'].lower() == folder_name.lower():
                return label['id']
        return 'INBOX'

    def _parse_email(self, msg_id):
        """Parse email message data"""
        msg = self.service.users().messages().get(
            userId='me', id=msg_id, format='full').execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        body = self._extract_email_body(msg['payload'])
        clean_body = self._clean_html(body)
        
        return {
            "subject": subject,
            "sender": sender,
            "body": clean_body,
            "date": date
        }

    def _extract_email_body(self, payload):
        """Recursively extract email body from payload"""
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
                elif 'parts' in part:
                    body = self._extract_email_body(part)
                    if body: break
        else:
            if 'data' in payload.get('body', {}):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        return body

    def _clean_html(self, html_content):
        """Extract text from HTML email content"""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)

    def detection_agent(self, email):
        """Detect suspicious content patterns"""
        try:
            prompt = ChatPromptTemplate.from_template(
                "Analyze this email for suspicious elements:\n"
                "Subject: {subject}\nSender: {sender}\n\n{body}\n\n"
                "Identify: 1. Urgent requests 2. Unusual sender addresses "
                "3. Grammar mistakes 4. Suspicious links/attachments. "
                "Output: List of findings."
            )
            chain = prompt | gpt4 | StrOutputParser()
            return chain.invoke({
                "subject": email["subject"],
                "sender": email["sender"],
                "body": email["body"][:10000]
            })
        except Exception as e:
            logger.error(f"Detection agent failed: {str(e)}")
            return f"Error in detection: {str(e)}"

    def format_analysis_agent(self, email, detection_result):
        """Analyze email structure and metadata"""
        try:
            prompt = ChatPromptTemplate.from_template(
                "Analyze email format based on detection report:\n\n"
                "Detection Report:\n{detection_report}\n\n"
                "Email Metadata:\nFrom: {sender}\nDate: {date}\n\n"
                "Check for: 1. Spoofed headers 2. Mismatched domains "
                "3. Unusual formatting 4. Hidden content. "
                "Output: Format risk score 0-10 with explanation."
            )
            chain = prompt | gpt4 | StrOutputParser()
            return chain.invoke({
                "detection_report": detection_result,
                "sender": email["sender"],
                "date": email["date"]
            })
        except Exception as e:
            logger.error(f"Format analysis failed: {str(e)}")
            return "5 - Error in analysis"

    def risk_assessment_agent(self, email, format_score):
        """Combine analysis for risk assessment"""
        try:
            prompt = ChatPromptTemplate.from_template(
                "Perform final risk assessment:\n\n"
                "Subject: {subject}\nFormat Risk: {format_score}\n\n"
                "Content Summary (truncated):\n{body}\n\n"
                "Output: Final risk score 0-100 with justification."
            )
            chain = prompt | gpt4 | StrOutputParser()
            return chain.invoke({
                "subject": email["subject"],
                "format_score": format_score,
                "body": email["body"][:5000]
            })
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return "50 - Error in assessment"

    def final_decision_agent(self, risk_assessment):
        """Determine if email should be flagged"""
        try:
            prompt = ChatPromptTemplate.from_template(
                "Based on risk assessment, should this email be flagged?\n"
                "Assessment: {risk_assessment}\n\n"
                "Decision Criteria: Flag if risk > 70 or critical threats detected.\n"
                "Output: ONLY 'YES' or 'NO'."
            )
            chain = prompt | gpt4 | StrOutputParser()
            decision = chain.invoke({"risk_assessment": risk_assessment}).strip()
            return decision.upper() == "YES"
        except Exception as e:
            logger.error(f"Decision agent failed: {str(e)}")
            return False

    def _move_to_flagged_label(self, msg_id):
        """Move email to Flagged_Suspicious label"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': [self.flagged_label_id]}
            ).execute()
            logger.info(f"Moved email {msg_id} to Flagged_Suspicious label")
        except Exception as e:
            logger.error(f"Failed to move email {msg_id} to flagged label: {str(e)}")

    def process_emails(self, folder="INBOX", limit=5):
        """Run email processing pipeline with error handling"""
        try:
            emails = self.fetch_emails(folder=folder, limit=limit)
            if not emails:
                logger.warning("No emails found to process")
                return []
                
            flagged_emails = []
               
            progress_bar = st.progress(0)
            total_emails = len(emails)
            
            for i, email in enumerate(emails):
                try:
                    msg_id = email['msg_id']
                    detection_result = self.detection_agent(email)
                    format_result = self.format_analysis_agent(email, detection_result)
                    risk_result = self.risk_assessment_agent(email, format_result)
                    
                    if self.final_decision_agent(risk_result):
                        self._move_to_flagged_label(msg_id)
                        local_file = self._save_flagged_email_locally(email, risk_result, msg_id)
                        flagged_emails.append({
                            "subject": email["subject"],
                            "sender": email["sender"],
                            "date": email["date"],
                            "risk_score": risk_result,
                            "msg_id": msg_id,
                            "local_file": local_file,
                            "original_email": email
                        })
                        
                    progress_bar.progress((i + 1) / total_emails)
                        
                except Exception as e:
                    logger.error(f"Failed to process email {email.get('subject')}: {str(e)}")
                    continue
                    
            return flagged_emails
            
        except Exception as e:
            logger.error(f"Processing pipeline failed: {str(e)}")
            st.error(f"Processing pipeline failed: {str(e)}")
            return []

def main():
    st.title("Email Flagging System")
    st.write("This application scans your Gmail inbox for potentially suspicious emails.")
    
    # Display debug info
    with st.expander("Debug Information"):
        st.write(f"Current working directory: {os.getcwd()}")
        st.write(f"Files in directory: {os.listdir()}")
        st.write(f"Email User: {os.getenv('EMAIL_USER')}")
    
    try:
        system = EmailFlaggingSystem()
        logger.info("System initialized successfully")
        
        # Input for number of emails to process
        email_limit = st.number_input("Number of emails to process", min_value=1, max_value=50, value=5)
        
        if st.button("Scan Emails"):
            with st.spinner("Processing emails..."):
                logger.info(f"Processing batch of {email_limit} emails...")
                flagged_emails = system.process_emails(limit=email_limit)
                
                st.subheader("Results")
                if not flagged_emails:
                    st.info("No suspicious emails found in this batch")
                else:
                    st.warning(f"Found {len(flagged_emails)} potentially suspicious emails:")
                    for i, email in enumerate(flagged_emails, 1):
                        with st.expander(f"Email {i}: {email['subject']}"):
                            st.write(f"**From:** {email['sender']}")
                            st.write(f"**Date:** {email['date']}")
                            st.write(f"**Risk Assessment:** {email['risk_score']}")
                            st.write(f"**Stored locally at:** {email['local_file']}")
                            st.write("**Note:** This email has been moved to the 'Flagged_Suspicious' label in your Gmail account.")
                            st.write("---")
                
                logger.info("Processing completed. See email_processing.log and flagged_emails folder for details")
                
    except Exception as e:
        logger.critical(f"System failed: {str(e)}", exc_info=True)
        st.error("CRITICAL ERROR: Check logs for details")
    

if __name__ == "__main__":
    main()

