# Email Automation for Private Credit Leads

This script automates the process of generating personalized emails for private credit leads using OpenAI's API.

## Features

- Reads contact information from a CSV file
- Uses OpenAI's API to generate personalized emails based on a template
- Customizes emails based on company name, industry focus, contact name, position, and notes
- Saves generated emails to a new CSV file
- Includes error handling and rate limiting to avoid API issues

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file to add your OpenAI API key and personal information

## Usage

1. Make sure your input CSV file is in the correct format with the following columns:
   - Company Name
   - Industry Focus
   - Contact Name
   - Position / Role
   - Notes

2. Run the script:
   ```
   python automate_email.py
   ```

3. The script will generate personalized emails for each contact and save them to `Generated_Emails.csv`

### Command-line Arguments

The script supports several command-line arguments for flexibility:

```
python automate_email.py [options]
```

Options:
- `--input`, `-i`: Path to the input CSV file (default: "Private Credit Leads - Private Credit Leads.csv")
- `--output`, `-o`: Path to the output CSV file (default: "Generated_Emails.csv")
- `--model`, `-m`: OpenAI model to use (default: "gpt-4")
- `--limit`, `-l`: Limit the number of emails to generate (default: 0 = no limit)
- `--dry-run`, `-d`: Dry run mode - do not make API calls, just print what would be done

Examples:
```
# Process only the first 5 contacts
python automate_email.py --limit 5

# Use a different input file
python automate_email.py --input my_contacts.csv

# Test the script without making API calls
python automate_email.py --dry-run
```

## Customization

You can customize the email template by editing the `EMAIL_TEMPLATE` variable in the script.

## Notes

- The script will skip contacts without a name
- You can adjust the OpenAI model and parameters in the `generate_email` function
- Make sure your OpenAI API key has sufficient credits
- The script includes retry logic and rate limiting to handle API errors 