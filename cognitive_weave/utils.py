# cognitive_weave_poc/cognitive_weave/utils.py

import os
from openai import AzureOpenAI

# --- Azure OpenAI Configuration ---
# IMPORTANT: The values below are hardcoded as per your request.
# For production, consider environment variables or a secure config management system.

# Define the ORIGINAL placeholder strings for comparison logic
_PLACEHOLDER_ENDPOINT = "YOUR_AZURE_OPENAI_ENDPOINT"
_PLACEHOLDER_KEY = "YOUR_AZURE_OPENAI_KEY"
_PLACEHOLDER_DEPLOYMENT = "YOUR_GPT4_DEPLOYMENT_NAME"

# --- Hardcoded Azure OpenAI Credentials ---
AZURE_OAI_ENDPOINT = ""
AZURE_OAI_KEY = ""
AZURE_OAI_DEPLOYMENT_GPT4 = "gpt-4"
API_VERSION = "2024-04-01-preview"
# --- End of Hardcoded Credentials ---

# Check if the current values are still the original placeholders
# This warning will now only trigger if the values above are accidentally reverted to the _PLACEHOLDER_ strings.
if AZURE_OAI_ENDPOINT == _PLACEHOLDER_ENDPOINT or \
   AZURE_OAI_KEY == _PLACEHOLDER_KEY or \
   AZURE_OAI_DEPLOYMENT_GPT4 == _PLACEHOLDER_DEPLOYMENT:
    print("="*80)
    print("CRITICAL WARNING: Azure OpenAI credentials in cognitive_weave/utils.py are still the original placeholders!")
    print("This should not happen if you have hardcoded your actual credentials above.")
    print("Please check the variable assignments for AZURE_OAI_ENDPOINT, AZURE_OAI_KEY, and AZURE_OAI_DEPLOYMENT_GPT4.")
    print("="*80)
elif AZURE_OAI_ENDPOINT == "" and \
     AZURE_OAI_KEY == "" and \
     AZURE_OAI_DEPLOYMENT_GPT4 == "gpt-4":
    print("="*80)
    print("INFO: Using the specific Azure OpenAI credentials hardcoded in cognitive_weave/utils.py.")
    print(f"  Endpoint: {AZURE_OAI_ENDPOINT}")
    print(f"  Deployment: {AZURE_OAI_DEPLOYMENT_GPT4}")
    print(f"  API Version: {API_VERSION}")
    print("  Note: Ensure these credentials are correct and the API key is valid (typically 32 characters).")
    print("="*80)


def get_azure_openai_client():
    """
    Initializes and returns an AzureOpenAI client.
    """
    # Validate that credentials are not the original placeholders before trying to connect
    if AZURE_OAI_ENDPOINT == _PLACEHOLDER_ENDPOINT or \
       AZURE_OAI_KEY == _PLACEHOLDER_KEY or \
       AZURE_OAI_DEPLOYMENT_GPT4 == _PLACEHOLDER_DEPLOYMENT:
        log_error("Cannot initialize Azure OpenAI client: Credentials are still set to original placeholders.")
        log_error("Please update cognitive_weave/utils.py with your actual Azure credentials.")
        raise ValueError("Azure OpenAI credentials are not configured.")

    try:
        client = AzureOpenAI(
            azure_endpoint=AZURE_OAI_ENDPOINT,
            api_key=AZURE_OAI_KEY,
            api_version=API_VERSION
        )
        return client
    except Exception as e:
        print(f"Error initializing Azure OpenAI client: {e}")
        print("Please ensure your Azure OpenAI endpoint, key, deployment name, and API version are correctly configured and valid in cognitive_weave/utils.py.")
        raise

# Example of a simple logger if needed (optional for this PoC)
def log_info(message: str):
    """Simple informational logger."""
    print(f"[INFO] {message}")

def log_error(message: str):
    """Simple error logger."""
    print(f"[ERROR] {message}")

