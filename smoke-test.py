# check logger
# from src.logger import logger

# def check_logging():
#     logger.info("Testing log file.")
#     logger.error("This is error log.")

# check_logging()

# ----------------------------------------------------

# check discover file
# from src.utils import discover_files
# from src.config import config
# df = discover_files(config.PROJECT_ROOT / "data/input", ["*.txt"])
# print(df.head())

# ----------------------------------------------------

from src.llm_manager import llm
from src.config import config
from src.schemas.customer_complaint_schema import CustomerComplaint

def test_complaint_schema_extraction():

    with open("prompts/parser_system_prompt.txt", "r", encoding="utf-8") as file:
        parser_system_prompt = file.read()

    with open("prompts/complaint_extraction_prompt.txt", "r", encoding="utf-8") as file:
        complaint_extraction_prompt = file.read()

    complaint_extraction_file_path = config.PROJECT_ROOT / "data" / "input" / "complaint_001.txt"

    response = llm.parse_document_with_llm(document_prompt=complaint_extraction_prompt,
                                system_prompt=parser_system_prompt,
                                file_path=complaint_extraction_file_path,
                                response_schema=CustomerComplaint)

    if(response['success']):
        print(response["content"].model_dump())
    else:
        print(response)

    return response["content"].model_dump()
    
# test_complaint_schema_extraction()

# ----------------------------------------------------

from src.schemas.email_schema import EmailDetails

def test_email_body_gen():

    with open("prompts/email_system_prompt.txt", "r", encoding="utf-8") as file:
        email_system_prompt = file.read()

    with open("prompts/customer_email_prompt.txt", "r", encoding="utf-8") as file:
        email_extraction_prompt = file.read()

    # parsing compaint
    complaint = test_complaint_schema_extraction()
    
    # creating email
    email_prompt = email_extraction_prompt.format(customer_complaint = complaint)

    email_result = llm.chat_completion(user_prompt = email_prompt,
                                 system_prompt=email_system_prompt, 
                                 response_schema = EmailDetails)
    if(email_result['success']):
        print(email_result["content"].model_dump())
    else:
        print(email_result)

    email = email_result["content"].model_dump()

    return email['subject'], email['body'], complaint['customer_email']

test_email_body_gen()  

