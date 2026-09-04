# define import and paths
from pathlib import Path
from tqdm.auto import tqdm

import sys
import warnings
import pandas as pd

from src.config import config
from src import utils
from src.llm_manager import llm
from src.schemas.customer_complaint_schema import CustomerComplaint
from src.schemas.email_schema import EmailDetails
from src.tools.email import send_email
from src.document_processor import process_documents

warnings.filterwarnings("ignore")

# paths
PROJECT_ROOT = Path(__file__).resolve().parent

print(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

INPUT_DOCUMENT_DIR = PROJECT_ROOT / config.PATHS['document_input']
STRUCTURED_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['structured_data_dir']
EMAIL_OUTPUT_DIR = PROJECT_ROOT / config.PATHS['email_data_dir']
OUTPUT_DATA_DIR = PROJECT_ROOT / config.PATHS['final_output']
PROMPTS_DIR = PROJECT_ROOT / "prompts"

def main():

    try:
        # read prompts
        parser_system_prompt, complaint_extraction_prompt, email_system_prompt, email_extraction_prompt = initializePrompts()

        # parse customer complaint document
        complaints_document_df = process_complaint_documents(parser_system_prompt, complaint_extraction_prompt)

        # write email content for customer
        email_df = generate_emails_for_complaints(complaints_document_df, email_system_prompt, email_extraction_prompt)

        # send email to customer
        email_result_df = send_email_to_customers(email_df)

        # generate final report
        summary_df = generate_customer_complaint_summary(email_result_df)

    except Exception as e :
        print(f"Pipeline failed : {e}")
        raise

def initializePrompts():

    OUTPUT_DATA_DIR.mkdir(parents=True,exist_ok=True)

    parser_system_prompt= utils.load_prompt(PROMPTS_DIR / "parser_system_prompt.txt" )
    complaint_extraction_prompt = utils.load_prompt(PROMPTS_DIR / "complaint_extraction_prompt.txt" )
    email_system_prompt = utils.load_prompt(PROMPTS_DIR / "email_system_prompt.txt" )
    email_extraction_prompt = utils.load_prompt(PROMPTS_DIR / "customer_email_prompt.txt" )

    return parser_system_prompt, complaint_extraction_prompt, email_system_prompt, email_extraction_prompt

def process_complaint_documents(parser_system_prompt, complaint_extraction_prompt):

    complaints_doc_df = utils.discover_files(INPUT_DOCUMENT_DIR)
    empty_complaint = {
        "customer_name" : None,
        "customer_email" : None,
        "customer_phone" : None,
        "complaint_category" : None,
        "complaint_description" : None,
        "resolution_provided" : None,
        "escalation_information" : None,
        "supporting_information" : None,
        "current_status": None 
    }

    complaints_doc_df, results = process_documents(
        complaints_doc_df=complaints_doc_df,
        extraction_prompt=complaint_extraction_prompt,
        system_prompt=parser_system_prompt,
        response_format=CustomerComplaint,
        default_response=empty_complaint
    )

    # save structured data
    structured_document_df = pd.concat([complaints_doc_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    output_file = STRUCTURED_OUTPUT_DIR / "complaint_structured_data.csv"
    utils.save_dataframe(structured_document_df, output_file)

    # structured data for processing
    final_complaint_df = complaints_doc_df.reset_index(drop=True)
    final_complaint_df["complaint_object"] = results

    return final_complaint_df

def generate_emails_for_complaints(complaints_document_df, email_system_prompt, email_extraction_prompt):

    complaints_document_df["email_generation"] = "Pending"
    results = []
    empty_email ={
        "email_subject":None,
        "email_body":None
    }
    email_df = pd.DataFrame()

    for index, row in tqdm(complaints_document_df.iterrows(), total=len(complaints_document_df), desc="Generating email content for customer..."):

        customer_complaint = row['complaint_object']
        email_df.loc[index,"customer_name"] = customer_complaint['customer_name']
        email_df.loc[index,"customer_email"] = customer_complaint['customer_email']
        email_df.loc[index,"email_subject"] = None
        email_df.loc[index,"email_body"] = None
        
        try: 
            email_prompt = email_extraction_prompt.format(customer_complaint=customer_complaint)

            response = llm.chat_completion(
                user_prompt=email_prompt,
                system_prompt=email_system_prompt,
                response_schema=EmailDetails
            )

            if response["success"]:
                email_object = response["content"].model_dump()
                results.append(email_object)
                complaints_document_df.loc[index,"email_generation"] = "Completed"
                email_df.loc[index,"email_subject"] = email_object['subject']
                email_df.loc[index,"email_body"] = email_object['body']
            else:
                results.append(empty_email)
                complaints_document_df.loc[index,"email_generation"] = "Failed"
                
        except Exception as e:
            results.append(empty_email)
            complaints_document_df.loc[index,"email_generation"] = f"Failed : {e}"

    # save emails generated for customer
    output_file = EMAIL_OUTPUT_DIR / "complaint_email_data.csv"
    utils.save_dataframe(email_df, output_file)

    final_df = pd.concat([complaints_document_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

    return final_df

def send_email_to_customers(email_df):

    email_df["email_sent"] = False

    for index, row in tqdm(email_df.iterrows(), total=len(email_df), desc="Sending emails to customer..."):
    
        try:
            complaint = row['complaint_object']

            email_sent = send_email(
                email_address = complaint['customer_email'],
                subject = row['subject'],
                body = row['body']
            )

            if email_sent:
                email_df.loc[index,"email_sent"] = True
            else:
                email_df.loc[index,"email_sent"] = False

        except Exception as e:
            email_df.loc[index,"email_sent"] = False

    return email_df

def generate_customer_complaint_summary(result_df):

    pass