from fastapi import FastAPI
from pydantic import BaseModel
# import openai
from openai import OpenAI # Import OpenAI client
import json
import os

# Initialize FastAPI app
app = FastAPI()

# Configure OpenAI API key
# It's best practice to load this from environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY") 


# Initialize OpenAI client
# It's best practice to load the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a request body model for incoming tickets
class TicketInput(BaseModel):
    ticket_text: str

# Your existing classification logic
def classify_and_summarize(ticket_text: str):
    if not client.api_key:
        raise ValueError("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        
    prompt = f"""
    Summarize the following support ticket and classify it:
    Ticket: {ticket_text}

    Respond in JSON:
    {{
        "summary": "...",
        "type": "bug" | "feature" | "billing"
    }}
    """
    
    # Use client.chat.completions.create for OpenAI v1.0.0+
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} # Ensure JSON output from API
    )

    # Accessing the content from the new response object structure
    result = json.loads(response.choices[0].message.content)
    return result

# Define your API endpoint
@app.post("/classify-ticket/")
async def classify_ticket_endpoint(ticket_input: TicketInput):
    try:
        classification_result = classify_and_summarize(ticket_input.ticket_text)
        return classification_result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred: " + str(e)}
