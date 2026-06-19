import os
import json  
# Built-in Python toolkit for converting between JSON text and Python dictionaries.

from dotenv import load_dotenv
from google import genai
from google.genai import types  
# "types" lets us configure extra settings for our API call (like forcing JSON output).

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

conversation = """
Doctor: What brings you in today?
Patient: I've had a sore throat and a cough for about 4 days. Also feeling pretty tired.
Doctor: Any fever?
Patient: Yeah, around 100.5 last night.
Doctor: Any trouble breathing or chest pain?
Patient: No, nothing like that.
Doctor: Let me take a look at your throat... it's a bit red, some mild swelling. Lungs sound clear.
Doctor: This looks like a viral upper respiratory infection. I'd recommend rest, fluids, and ibuprofen for fever. Come back if symptoms get worse or last more than 10 days.
"""

prompt = f"""You are a medical scribe assistant. Convert the following doctor-patient 
conversation into a SOAP note. Respond with ONLY a JSON object with exactly these 
four keys: "subjective", "objective", "assessment", "plan". No extra text, no markdown.

Conversation:
{conversation}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"  
        # This tells Gemini: "don't just write prose, return valid JSON only."
        # It's a setting on the API itself, not just a polite request in the prompt.
    )
)

note = json.loads(response.text)  
# json.loads() takes the JSON text the AI sent back and converts it into
# an actual Python dictionary we can work with — stored here as "note".

# Now we can access each part individually:
print("SUBJECTIVE:")
print(note["subjective"])
print()

print("OBJECTIVE:")
print(note["objective"])
print()

print("ASSESSMENT:")
print(note["assessment"])
print()

print("PLAN:")
print(note["plan"])