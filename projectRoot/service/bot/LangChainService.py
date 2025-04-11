import os
import re
import dto.Response as resp
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
from langchain.memory import ChatMessageHistory
import Utils
import service.bot.LogService as log
import datetime

PRINT_LOG = False
MODEL = 'openai'
#MODEL = 'anthropic'
TOKEN_REGEX = r"TOKEN -?\d+(\.\d+)?"
INFO_REGEX_ANGULAR = r"<(.*?)>"
# Regex to find JSON objects (limited to one level of nesting)
INFO_REGEX_CURLY = r'\{[^{}]*\}(?:,\s*\{[^{}]*\})*'

# Load environment variables from .env file
# Other available models:
# https://openai.com/api/pricing/
# gpt-3.5-turbo-0125
# gpt-4o-mini
# gpt-4o-2024-08-06 *
# gpt-4
# chatgpt-4o-latest
# gpt-4o
# o3-mini


#claude-3-sonnet-20241022 *
load_dotenv(find_dotenv())

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-2024-08-06")
if(MODEL == 'anthropic'):
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    llm = ChatAnthropic(model='claude-3-5-sonnet-20241022')

def get_prompt(input_prompt,memory):
    if(memory != None):
        return ChatPromptTemplate.from_messages(
            [
                ("system", input_prompt),
                MessagesPlaceholder(variable_name="memory"),
                ("human", "{query}"),
            ]
        )
    else:
        return ChatPromptTemplate.from_messages(
            [
                ("system", input_prompt),
                ("human", "{query}"),
            ]
        )
    
def execute_chain(input_prompt, input_query, temperature, userData, memory = None, memory_enabled = False):
    log.save_log(input_query, datetime.datetime.now(), "User", userData.id, PRINT_LOG)
    log.save_log(input_prompt, datetime.datetime.now(), "System: input_prompt", userData.id, PRINT_LOG)
    llm.temperature = temperature

    # Initialize memory if it is not provided and required
    if memory == None and memory_enabled:
        memory = ChatMessageHistory()
        memory.add_user_message(input_prompt)

    prompt = get_prompt(input_prompt,memory)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    if(memory != None):
        log.save_log(memory, datetime.datetime.now(), "System: memory", userData.id, PRINT_LOG)
        answer = chain.invoke({ "query": input_query, "memory": memory.messages })
    else:
        answer = chain.invoke({ "query": input_query })
    
    action = get_token(answer)
    info = get_info(answer)
    answer = clean_answer_from_token_and_info(answer, info)
    if(memory != None):
        memory.add_user_message(input_query)
        memory.add_ai_message(answer)
        
    response = resp.Response(answer,action,info,memory,'')
    log.save_log(response, datetime.datetime.now(), "Agent "+MODEL, userData.id, PRINT_LOG)
    return response

def get_token(answer):
    action = re.search(TOKEN_REGEX, answer)
    action = action.group()
    return action

def get_info(answer):
    info_angular = re.search(INFO_REGEX_ANGULAR, answer)
    if info_angular != None:
        info_angular = info_angular.group()
    else:
        info_angular = ""

    info_curly = re.search(INFO_REGEX_CURLY, answer)
    if info_curly != None:
        info_curly = info_curly.group()
    else:
        info_curly = ""

    return info_angular + " " + info_curly

def clean_answer_from_token_and_info(answer, info):
    answer = re.sub(TOKEN_REGEX, "", answer)
    answer = re.sub(INFO_REGEX_ANGULAR, "", answer)
    answer = re.sub(INFO_REGEX_CURLY, "", answer)
    answer = Utils.clean_json_string(answer)

    # Remove leading and trailing whitespace when info is not empty
    # this because in this situation the answer will be empty, so must ensure that there are no leading or trailing whitespaces
    if(info != ""):
        answer = answer.strip()
    return answer