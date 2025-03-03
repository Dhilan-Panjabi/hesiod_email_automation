import csv
import os
import pandas as pd
import time
import argparse
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file (create this file with your OpenAI API key)
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Email template
EMAIL_TEMPLATE = """
Subject: AI-Powered Deal Due Diligence Platform  
Dear [Recipient's Name],  
I know you're incredibly busy and get a lot of messages, so this will only take 60 seconds to read.  
I'm developing a platform that uses AI to streamline and enhance deal due diligence for private credit firms, helping you save time, reduce risk, and identify opportunities faster. The insights we've gained from AI-driven data analysis could be incredibly valuable for your investment process.  
Have you ever thought about how AI could transform due diligence for private credit deals? I think our platform could add significant value to your firm, and I'd love to discuss whether you'd be interested in exploring a partnership or pilot.  
I totally understand if you're too busy to respond. Even a one or two-line reply will completely make my day.  
Best regards,
[Your Full Name]
[Your Position/Title]
[Your Company/Startup Name, if applicable]
[Your Email Address]
[Your Phone Number, optional]
"""

# Your information - get from environment variables or use defaults
YOUR_NAME = os.getenv("YOUR_NAME", "Your Full Name")
YOUR_POSITION = os.getenv("YOUR_POSITION", "Your Position/Title")
YOUR_COMPANY = os.getenv("YOUR_COMPANY", "Your Company/Startup Name")
YOUR_EMAIL = os.getenv("YOUR_EMAIL", "your.email@example.com")
YOUR_PHONE = os.getenv("YOUR_PHONE", "Your Phone Number")

def generate_email(company_name, industry_focus, contact_name, position, notes, model="gpt-4"):
    """Generate a personalized email using OpenAI API"""
    
    # Skip if contact name is empty
    if not contact_name or pd.isna(contact_name):
        return None
    
    # Prepare prompt for OpenAI
    prompt = f"""
    Generate a personalized email based on the following template and information:
    
    Template:
    {EMAIL_TEMPLATE}
    
    Information:
    - Recipient's Company: {company_name}
    - Industry Focus: {industry_focus}
    - Recipient's Name: {contact_name}
    - Recipient's Position: {position}
    - Notes about recipient: {notes if notes and not pd.isna(notes) else "No specific notes"}
    
    Please personalize the email to make it relevant to their industry focus ({industry_focus}) and position ({position}).
    Replace [Recipient's Name] with {contact_name}.
    Replace [Your Full Name] with {YOUR_NAME}.
    Replace [Your Position/Title] with {YOUR_POSITION}.
    Replace [Your Company/Startup Name, if applicable] with {YOUR_COMPANY}.
    Replace [Your Email Address] with {YOUR_EMAIL}.
    Replace [Your Phone Number, optional] with {YOUR_PHONE}.
    
    Make the email concise, professional, and personalized based on the recipient's information.
    """
    
    # Retry mechanism for API calls
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,  # Use the model passed as parameter
                messages=[
                    {"role": "system", "content": "You are an assistant that generates personalized professional emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error generating email for {contact_name}, retrying in {retry_delay} seconds... ({e})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to generate email for {contact_name} after {max_retries} attempts: {e}")
                return f"Error generating email: {e}"

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate personalized emails for private credit leads.')
    parser.add_argument('--input', '-i', default="Automate_email/Private Credit Leads - Private Credit Leads.csv",
                        help='Path to the input CSV file (default: Private Credit Leads - Private Credit Leads.csv)')
    parser.add_argument('--output', '-o', default="Generated_Emails.csv",
                        help='Path to the output CSV file (default: Generated_Emails.csv)')
    parser.add_argument('--model', '-m', default="gpt-4",
                        help='OpenAI model to use (default: gpt-4)')
    parser.add_argument('--limit', '-l', type=int, default=0,
                        help='Limit the number of emails to generate (default: 0 = no limit)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Dry run mode - do not make API calls, just print what would be done')
    
    args = parser.parse_args()
    
    # Define paths from arguments
    input_csv_path = args.input
    output_csv_path = args.output
    
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv_path)
        print(f"Successfully read {len(df)} rows from {input_csv_path}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Create a new dataframe for the output
    output_data = []
    
    # Process each row in the CSV
    total_contacts = 0
    successful_emails = 0
    
    # Apply limit if specified
    if args.limit > 0:
        df = df.head(args.limit)
        print(f"Limiting to first {args.limit} rows")
    
    for index, row in df.iterrows():
        company_name = row.get('Company Name', '')
        industry_focus = row.get('Industry Focus', '')
        contact_name = row.get('Contact Name', '')
        position = row.get('Position / Role', '')
        notes = row.get('Notes', '')
        
        # Skip rows without contact names
        if not contact_name or pd.isna(contact_name):
            continue
        
        total_contacts += 1
        print(f"[{index+1}/{len(df)}] Generating email for {contact_name} at {company_name}...")
        
        # Generate email (or simulate in dry run mode)
        if args.dry_run:
            print(f"  [DRY RUN] Would generate email for {contact_name} with data: {company_name}, {industry_focus}, {position}")
            print(f"  [DRY RUN] Would use model: {args.model}")
            email_content = f"[DRY RUN] Sample email for {contact_name}"
            successful_emails += 1
        else:
            email_content = generate_email(company_name, industry_focus, contact_name, position, notes, model=args.model)
        
        if email_content and not email_content.startswith("Error generating email"):
            successful_emails += 1
            output_data.append({
                'Company Name': company_name,
                'Contact Name': contact_name,
                'Email Content': email_content
            })
            
            # Add a small delay to avoid rate limiting (not needed in dry run)
            if not args.dry_run:
                time.sleep(0.5)
    
    # Create output dataframe and save to CSV
    if output_data:
        output_df = pd.DataFrame(output_data)
        output_df.to_csv(output_csv_path, index=False)
        print(f"Successfully generated {len(output_data)} emails and saved to {output_csv_path}")
    else:
        print("No emails were generated. Check the input data and API connection.")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total contacts processed: {total_contacts}")
    print(f"Successful emails generated: {successful_emails}")
    print(f"Failed emails: {total_contacts - successful_emails}")

if __name__ == "__main__":
    main()
