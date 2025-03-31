# RAG Implementation using OpenAI's ChatGPT API

# Step 1: Import necessary libraries
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Step 2: Load and verify the OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

# Step 3: Helper function to read and extract text from a JSON file
def extract_all_text_from_json(json_path):
    def extract_text(data):
        if isinstance(data, dict):
            text = ""
            for key, value in data.items():
                text += f"{key}: "
                text += extract_text(value)
            return text
        elif isinstance(data, list):
            text = ""
            for item in data:
                text += extract_text(item)
            return text
        elif isinstance(data, str):
            return data + "\n"
        else:
            return ""

    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    return extract_text(data).strip()

# Step 4: Retrieve documents for RAG (currently just the extracted text)
def retrieve_documents():
    return [extracted_text]

# Step 5: Function to generate response using ChatGPT
def generate_response(query, mode="assisted"):
    # Retrieve documents
    retrieved_docs = retrieve_documents()

    
    # Construct the appropriate prompt
    if mode == "strict":
        prompt = (
            "Based on the following documents:\n"
            +"\n".join(retrieved_docs)
            + f"Answer the question: {query}"
            + "If the information is not present in the provided documents, clearly respond:"
            + " 'The requested information is not available in the provided documents.'"
            + " Do NOT provide answers from your own knowledge or other sources."
        )
    else:  # assisted mode
        prompt = (
            "Based on the following documents:\n"
            + "\n".join(retrieved_docs)
            + f"Answer the question: {query}"
            + "Provide a detailed answer."
            + " Don't justify your answers."
            + " Don't give information not mentioned in the CONTEXT INFORMATION."
            + " Do not say 'according to the context' or 'mentioned in the context' or similar."
        )

    # Call OpenAI API

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=1500,
    stream=True
)

    # Print the generated response (streaming mode)
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="")

# Step 6: Extract text from JSON file
#local_file_path = "./intent_api_2_3_7.json"  # Adjust if needed
local_file_path = "./authentication.json"
extracted_text = extract_all_text_from_json(local_file_path)


# Step 7: Interactive query loop with mode selector
while True:
    user_query = input("Enter your query (To exit, input 'done'): ")
    if user_query.lower() == "done":
        exit("Exiting the program")

    mode_input = input("Choose mode - type 'assisted' or 'strict': ").strip().lower()
    if mode_input not in ["assisted", "strict"]:
        print("Invalid mode selected. Defaulting to 'assisted'.")
        mode_input = "assisted"

    generate_response(user_query, mode=mode_input)

