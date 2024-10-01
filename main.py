import streamlit as st
import os
import google.auth
import time
import tomli

from translator import TranslationEntity

from bs4 import BeautifulSoup

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.cloud import bigquery
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

# get the config form file
with open(".streamlit/settings.toml", "rb") as f:
    settings = tomli.load(f)

# Set Vertex AI
generation_config = {
    "max_output_tokens": settings['model']['max_output_tokens'],
    "temperature": settings['model']['temperature'],
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

# get dictionaries of languages
languages_from = settings['languages']['lang_from']
languages_to = settings['languages']['lang_to']

# Retrieve the JSON key file path from Streamlit Secrets
key_path = st.secrets["google_key_path"]

# Set the environment variable to point to the key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

# Authenticate using the key file
credentials, project_id = google.auth.default()

client = bigquery.Client()

st.set_page_config(
    page_title="Babelfish AI",
    layout="wide")

def initialize():
    if 'langFrom' not in st.session_state:
        st.session_state['langFrom'] = settings['languages']['lang_from'][0]
    if 'langTo' not in st.session_state:
        st.session_state['langTo'] = settings['languages']['lang_to'][0]

    print ("end of initialize")

def query_bigquery(hash_value):

    tableid = settings['bigquery']['tableid']

    query = f"""
        SELECT *
        FROM `{tableid}`
        WHERE `hash` = '{hash_value}'
    """
    
    st.write(query)

    query_job = client.query(query)
    results = query_job.result()

    # Convert results to a list of rows
    rows = list(results)

    return rows if rows else None

def insert_into_bigquery(entity):
    """Inserts a translation entity into the BigQuery table.

    Args:
        entity: A TranslationEntity object containing the translation data.
    """

    table_id = settings['bigquery']['tableid']  # Get table ID from settings

    row_to_insert = {
        "hash": entity.hash,
        "original": entity.original,
        "translated": entity.translated,
        "langFrom": entity.langFrom,
        "langTo": entity.langTo
    }

    errors = client.insert_rows_json(table_id, [row_to_insert])  # Insert as a single row
    if errors == []:
        print(f"New row inserted with hash: {entity.hash}")
    else:
        print(f"Encountered errors while inserting row: {errors}")

def generate_answer(content, langFrom, langTo):
    INSTRUCTIONS = f"""
    You are a translation specialist working for a medical organization. Your primary responsibility is to translate medical text with the utmost accuracy and safety. 

    **Guidelines:**

    - **Allowed language:** Allow usage of the words about health condition, gender, diseases, etc. You are working in a medical environment and that is correct to use such words.
    - **Medical Accuracy:** Prioritize medical accuracy in your translations.
    - **Faithful Translation:** Translate all text content faithfully and accurately, focusing solely on the provided English text.
    - **Translation:** Do not comment on the original text and it's context, jus provide translated text.
    - **Do not add HTML Tags** 
    - **Language Pair:** Translate from {langFrom} to {langTo}.
    """
  
    vertexai.init(project=f"{project_id}", location=f"{settings['model']['location']}")
    model = GenerativeModel(
        f"{settings['model']['name']}",
        system_instruction=[INSTRUCTIONS]
    )
    
    responses = model.generate_content(
        [content],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    full_response = ""
    for response in responses:
        full_response += response.text
        print(response.text, end="")

    # sleep before calling next 
    # time.sleep(settings['model']['sleep_time'])

    return(full_response)

def translate(langFrom, langTo, html_content):
    print(f"Translation from {langFrom} to {langTo} in progress...")
    #progress_text = () f"Translation from {langFrom} to {langTo} in progress..."
    #progress_bar = st.progress(0, text=progress_text)

    soup = BeautifulSoup(html_content, 'html.parser')
    
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span']):

        print (f'TAG   : {tag.string}')

        if tag.string is not None:

            entity = TranslationEntity(original=tag.string, 
                                    langFrom=langFrom, 
                                    langTo=langTo)
            
            print ('='*40)
            print (f'HASH  : {entity.hash}')
            print (f'ORIG  : {entity.original}')
            print (f'TRANS : {entity.translated}')
            print (f'LNFR  : {entity.langFrom}')
            print (f'LTO   : {entity.langTo}')

            # here goes SQL query for hash
            results = query_bigquery(entity.hash)
            if results:
                for row in results:
                    entity.translated = row.translated
                    print (f'CACHED: {entity.translated}')

            else:
                st.write (f"need to translate {entity.original}")
                print (f'Need to translate from {langFrom} to {langTo}...')
                entity.translated = generate_answer(entity.original, langFrom=langFrom, langTo=langTo)
                print (f'NEW   : {entity.translated}')
                insert_into_bigquery(entity)

            print (f'TRN   : {entity.translated}')
            # Replace the original text with the translated text
            tag.string.replace_with(entity.translated)

        #progress_bar.progress(i + 1, text=progress_text)
        #time.sleep(0.1)
    
    #progress_bar.empty()
    
source_file = st.file_uploader("Choose a file for translation", type=[".html", ".htm"])

col1, col2 = st.columns(2)

with col1:

    st.session_state['langFrom'] = st.selectbox("Translate from:", options=languages_from)

    if source_file is not None:
        html_content = source_file.read().decode("utf-8")
        st.components.v1.html(html_content, height=settings['display']['height'], scrolling=True)
        if st.button("Translate"):
            on_click=translate(langFrom=st.session_state['langFrom'], 
                               langTo=st.session_state['langTo'], 
                               html_content=html_content)
    else:
        st.write("Please upload an HTML file.")

with col2:

    st.session_state['langTo'] = st.selectbox("Translate to:", options=languages_to)

    st.html("<p>Here goes TARGET html</p>")