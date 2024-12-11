# AZ Demo Translation

This repository demonstrates a fully integrated solution that harnesses the power of Microsoft Azure’s AI services—all running behind a serverless **Azure Function** backend—to enhance multilingual document comprehension and user experience. By simply uploading a PDF through the front-end interface:

1. Extracts text from documents using **Azure Document Intelligence**.
2. Translates that content into English using **Azure Translator**.
3. Summarizes and describes the translated text **with Azure OpenAI**.

The included front end is built with Streamlit, serving as a stand-in example UI for demonstration purposes. You can easily replace it with any preferred frontend framework or integrate the backend endpoints directly into your existing applications. The goal is to showcase how Azure services and a serverless architecture can seamlessly transform raw documents into rich, accessible, and interactive content for end-users.

## Prerequisites

1. ### Azure Subscription:

    You’ll need an active Azure subscription to provision and manage the required Azure services.

2. ### Required Azure Resources:

    - [Azure FunctionApp](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview): To host and run the serverless backend.
    - [Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence): For text extraction from uploaded documents.
    - [Azure AI Translator](https://azure.microsoft.com/en-us/products/ai-services/ai-translator): For translating extracted text into English.
    - [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) with gpt4o model deployed: To summarize and describe the translated text.

3. ### Local Development Environment

    - **Python 3.9+**: For running the Azure Function locally and Streamlit front end.
    - [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)" To develop and test the Azure Function locally.
    - [Streamlit](): For running the example front-end interface (if you choose to use it).
    - **Pip/Requirements**: The necessary Python packafes listed in *requirements.txt*

4. ### Credentials and Configuration:

    - Make sure you have the keys and endpoints for all the Azure resources mentioned above stored securely (e.g., in environment variables or Azure Key Vault).
    - Update your environment variables and configuration files accordingly before running the solution.

5. ### Environmental Variables

    You’ll need to set environment variables for keys and endpoints for each Azure resource. For example:

    **Front End Variables** /frontend/.env

    ```bash
    AZURE_FUNCTION_ENDPOINT="<Azure Function endpoint w/ Key>
    ```

    | Environment Variable                   | Description                                  | Example Value                                             |
    |----------------------------------------|----------------------------------------------|-----------------------------------------------------------|
    | AZURE_FUNCTION_ENDPOINT                | Azure Function App HTTP trigger URL. Including the function key *?code<>=*| https://translatorFunction.azurewebsites.net/api/translate?code=<functionKey>|

    *** Azure Function Variables** /function/local.settings.json

    ```json
    "AZURE_OPENAI_DEPLOYMENT":"gpt4o",
    "AZURE_OPENAI_ENDPOINT": "https://<instance_name>.openai.azure.com",
    "AZURE_OPENAI_KEY": "",
    "AZURE_OPENAI_API_VERSION":"2023-05-15",
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT":"https://<instance_name>.cognitiveservices.azure.com/",
    "AZURE_DOCUMENT_INTELLIGENCE_KEY": "",
    "AZURE_TRANSLATE_ENDPOINT":"https://<translate_endpoint_name>.cognitiveservices.azure.com/",
    "AZURE_TRANSLATE_KEY":"",
    "AZURE_TRANSLATE_REGION":"eastus"
    ```

    | Environment Variable                   | Description                                  | Example Value                                             |
    |----------------------------------------|----------------------------------------------|-----------------------------------------------------------|
    | `AZURE_OPENAI_DEPLOYMENT`              | Azure OpenAI deployment name                 | `gpt4o`                                                   |
    | `AZURE_OPENAI_ENDPOINT`                | Azure OpenAI endpoint URL                    | `https://<instance_name>.openai.azure.com`                |
    | `AZURE_OPENAI_KEY`                     | Azure OpenAI subscription key                | *(Your Azure OpenAI Key)*                                 |
    | `AZURE_OPENAI_API_VERSION`             | Azure OpenAI API version                     | `2023-05-15`                                              |
    | `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure Document Intelligence endpoint URL      | `https://<instance_name>.cognitiveservices.azure.com/`     |
    | `AZURE_DOCUMENT_INTELLIGENCE_KEY`      | Azure Document Intelligence subscription key  | *(Your Document Intelligence Key)*                        |
    | `AZURE_TRANSLATE_ENDPOINT`             | Azure Translator endpoint URL                | `https://<translate_endpoint_name>.cognitiveservices.azure.com/` |
    | `AZURE_TRANSLATE_KEY`                  | Azure Translator subscription key             | *(Your Translator Key)*                                   |
    | `AZURE_TRANSLATE_REGION`               | Azure Translator resource region             | `eastus`                                                  |