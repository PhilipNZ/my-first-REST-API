This guide will show you how to package your Python tickets classifier into a REST API using FastAPI and deploy it on a free hosting server (Render.com).

### Step 1: Set up your FastAPI application

First, you'll need to create a new file named `main.py` for your FastAPI application.

**1.1. Create `main.py`:**

```python
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import json
import os

# Initialize FastAPI app
app = FastAPI()

# Configure OpenAI API key
# It's best practice to load this from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY") 

# Define a request body model for incoming tickets
class TicketInput(BaseModel):
    ticket_text: str

# Your existing classification logic
def classify_and_summarize(ticket_text: str):
    if not openai.api_key:
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
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    result = json.loads(response.choices[0].message['content'])
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

```

**1.2. Create `requirements.txt`:**

You'll need a `requirements.txt` file to list the Python dependencies for your project.

```
fastapi
uvicorn
openai
```

### Step 2: Test your API locally

Before deploying, it's good practice to test your API on your local machine.

**2.1. Install dependencies:**

Open your terminal or command prompt and navigate to your project directory. Then, run:

```bash
pip install -r requirements.txt
```

**2.2. Set your OpenAI API Key:**

Before running the app, set your OpenAI API key as an environment variable. Replace `YOUR_OPENAI_API_KEY` with your actual key.

  * **Linux/macOS:**
    ```bash
    export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
  * **Windows (Command Prompt):**
    ```bash
    set OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
  * **Windows (PowerShell):**
    ```powershell
    $env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```

**2.3. Run the application:**

```bash
uvicorn main:app --reload
```

You should see output indicating that the server is running. Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation (Swagger UI).

You can test your endpoint directly from this page by clicking on `/classify-ticket/`, then "Try it out", entering a sample ticket text in the request body, and clicking "Execute".

### Step 3: Deploy to Render.com (Free Tier)

Render.com offers a generous free tier for web services, which is suitable for this type of API.

**3.1. Prepare for Deployment:**

  * **Create a Git Repository:** Initialize a Git repository in your project directory and push your code (`main.py` and `requirements.txt`) to a service like GitHub or GitLab. Render will connect to this repository.

    ```bash
    git init
    git add .
    git commit -m "Initial commit for FastAPI classifier"
    git branch -M main
    git remote add origin <your_repository_url>
    git push -u origin main
    ```

**3.2. Deploy on Render:**

1.  **Sign up/Log in to Render:** Go to [https://render.com/](https://render.com/) and sign up or log in. You can use your GitHub account for easy integration.
2.  **New Web Service:** From your dashboard, click "New" and then "Web Service".
3.  **Connect to your Git Repository:** Select "Build and deploy from a Git repository" and connect your GitHub/GitLab account. Choose the repository you created earlier.
4.  **Configure your service:**
      * **Name:** Give your service a descriptive name (e.g., `ticket-classifier-api`).
      * **Region:** Choose a region close to you or your users.
      * **Branch:** `main` (or whatever your primary branch is).
      * **Root Directory:** Leave empty if your `main.py` is at the root.
      * **Runtime:** Python 3
      * **Build Command:** `pip install -r requirements.txt`
      * **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
          * **Important:** Render injects the port as an environment variable `$PORT`.
      * **Instance Type:** Select "Free".
5.  **Add Environment Variable:**
      * Go to the "Environment" section.
      * Add a new environment variable:
          * **Key:** `OPENAI_API_KEY`
          * **Value:** Your actual OpenAI API key.
6.  **Create Web Service:** Click "Create Web Service".

Render will now start building and deploying your application. You can monitor the build logs in the Render dashboard. Once the deployment is successful, Render will provide you with a public URL for your API.

### Step 4: Using your Deployed API

Once deployed, you can access your API at the URL provided by Render (e.g., `https://your-service-name.onrender.com`). You can test it using tools like Postman, curl, or directly through the `/docs` endpoint (Swagger UI) if you append `/docs` to your Render URL.

**Example `curl` request:**

```bash
curl -X POST "https://your-service-name.onrender.com/classify-ticket/" \
     -H "Content-Type: application/json" \
     -d '{"ticket_text": "My account was charged twice for the same subscription."}'
```

Replace `https://your-service-name.onrender.com` with your actual Render service URL.

This setup provides a scalable and accessible REST API for your ticket classifier, ready for others to integrate with their applications.