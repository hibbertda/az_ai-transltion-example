import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult
from azure.ai.translation.text import TextTranslationClient
import logging
import os
import json
import requests
from openai import AzureOpenAI

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
logging.basicConfig(level=logging.INFO)

def docintel_extract(result):
    # Extract key-value pairs
    kv_dict = {}
    if hasattr(result, 'key_value_pairs'):
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key_text = kv_pair.key.content
                value_text = kv_pair.value.content
                kv_dict[key_text] = value_text

    # Aggregate text content
    text_content = ""
    if hasattr(result, 'pages'):
        for page in result.pages:
            for line in page.lines:
                text_content += line.content + " "

    # Prepare the response
    response_data = {
        "key_value_pairs": kv_dict,
        "text_content": text_content.strip()
    }

    return response_data

def azure_translate(document):
    endpoint = os.environ.get("AZURE_TRANSLATE_ENDPOINT")
    key = os.environ.get("AZURE_TRANSLATE_KEY")
    region = os.environ.get("AZURE_TRANSLATE_REGION")

    # Create a Text Translation client
    client = TextTranslationClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key),
        region=region
        )

    # Translate text w/ auto language detection
    try:
        to_language = ["en"]  # Specify the target language
        body = [{"text": document}]

        response_data = []

        response = client.translate(body=body, to_language=to_language)
        translation = response[0] if response else None

        if translation:
            detectec_language = translation.detected_language
            if detectec_language:
                logging.info(f"Detected language: {detectec_language.language}, with score {detectec_language.score}")
            for translated_text in translation.translations:
                logging.info(f"Translated text: {translated_text.text}")
                
                # summarize the translated text
                summary = ai_summary(translated_text.text)    

                # describe the translated text
                description = ai_describe(translated_text.text)            

                response_data.append({
                    "original_text": document,
                    "detected_language": detectec_language.language,
                    "detected_language_score": detectec_language.score,
                    "translated_text": translated_text.text,
                    "summary": summary,
                    "description": description
                })

            return response_data
    
    except Exception as e:
        logging.error(f"Error translating text: {str(e)}")
        return None

def ai_summary(input):

    llmclient = AzureOpenAI(
        api_key = os.environ.get("AZURE_OPENAI_KEY"),
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION"),
        #base_url=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        #azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )

    try:
        response = llmclient.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a professional summarizer. Summarize the following text."},
                {"role": "user", "content": input}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"Error generating summary: {str(e)}")
        return None

def ai_describe(input):
    llmclient = AzureOpenAI(
        api_key = os.environ.get("AZURE_OPENAI_KEY"),
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION"),
        #base_url=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        #azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )

    system_prompt = """

        Read the following document and provide a concise summary that captures its main topic, purpose, 
        intended audience, and any key points or recommendations it presents.
        
        """

    try:
        response = llmclient.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"Error generating description: {str(e)}")
        return None

@app.route(route="translate")
def translate(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    document_content = req.get_body()

     # Get file from request
    try:
        if document_content:
            logging.info("File received successfully.")
        elif not document_content:
            return func.HttpResponse(
                "No file found in the request.",
                status_code=400
            )

    except Exception as e:
        return func.HttpResponse(
            f"Error processing the request: {str(e)}",
            status_code=500
        )
    
    # Call Azure Document Intelligence API
    # Set the endpoint and key for the Document Intelligence API
    endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    # Create a Document Intelligence client
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
        )

    # set features based on file type

    # Check the file type and set features accordingly
    if req.headers.get("Content-Type") == "application/pdf":
        features = [DocumentAnalysisFeature.KEY_VALUE_PAIRS]
    elif req.headers.get("Content-Type") == "image/jpeg":
        features = [DocumentAnalysisFeature.KEY_VALUE_PAIRS]
    elif req.headers.get("Content-Type") == "image/png":
        features = [DocumentAnalysisFeature.KEY_VALUE_PAIRS]
    elif req.headers.get("Content-Type") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        features = []
    else:
        return func.HttpResponse(
            "Unsupported file type.",
            status_code=400
        )

    # Call the API to analyze the document
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        analyze_request=document_content,
        features=features,
        content_type="application/octet-stream",
    )
    result = poller.result()

    # Extract key-value pairs and text content from the result
    response_data = docintel_extract(result)


    # Check if the operation was successful
    if not result:
        return func.HttpResponse(
            "Error analyzing the document.",
            status_code=500
        )

    az_translate = azure_translate(response_data["text_content"])

    # return json response
    return func.HttpResponse(
        #json.dumps(response_data),
        json.dumps(az_translate, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )