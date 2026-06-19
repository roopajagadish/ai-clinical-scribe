import os
import json
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

NOTES_FILE = "notes.json"  
# The name of the file we'll save all past notes into.

def load_notes():
    # Reads notes.json and returns its contents as a Python list.
    if os.path.exists(NOTES_FILE):  
        # os.path.exists() checks whether the file already exists before trying to open it.
        with open(NOTES_FILE, "r") as f:
            return json.load(f)  
            # json.load() reads the file's JSON text and converts it into a Python list/dict.
    return []  
    # If the file doesn't exist yet (first time ever running this), return an empty list.

def save_notes(notes):
    # Writes the full list of notes back into notes.json, overwriting old contents.
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)  
        # json.dump() converts our Python list back into JSON text and writes it to the file.
        # indent=2 just makes the saved file nicely readable if you ever open it yourself.

st.title("Clinical Scribe Assistant")
st.write("Paste a doctor-patient conversation below to generate a SOAP note.")

conversation = st.text_area("Conversation", height=250)

if st.button("Generate SOAP Note"):
    if conversation.strip() == "":
        st.warning("Please paste a conversation first.")
    else:
        with st.spinner("Generating note..."):
            prompt = f"""You are a clinical documentation assistant. Your ONLY job is to convert 
            the conversation below into a structured SOAP note based EXACTLY on what was said.

            CRITICAL RULES:
            - Do NOT add any medical information, diagnoses, or recommendations that were not 
              explicitly stated in the conversation.
            - If a SOAP section has no relevant information in the conversation, write 
              "Not discussed" for that section rather than guessing or inventing content.
            - Preserve clinical accuracy — do not soften, exaggerate, or reinterpret what was said.
            - Ignore filler words, false starts, or repeated phrases — write in clean clinical 
              language, but do not change the actual meaning or add information.
            - Use standard medical abbreviations where appropriate but only if it doesn't reduce clarity.

            Respond with ONLY a JSON object with exactly these four keys: 
            "subjective", "objective", "assessment", "plan". No extra text, no markdown.

            Conversation:
            {conversation}
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            note = json.loads(response.text)
            st.session_state.current_note = note  
            # Saves the generated note into session_state, under the name "current_note" —
            # this is what keeps it from disappearing when you click other buttons next.

if "current_note" in st.session_state:  
    # Only show the editable fields if a note has actually been generated this session.
    st.subheader("Review & Edit Note")
    st.caption("Edit any field below before saving — the AI's draft is a starting point, not a final record.")

    edited_subjective = st.text_area("Subjective", value=st.session_state.current_note["subjective"])
    edited_objective = st.text_area("Objective", value=st.session_state.current_note["objective"])
    edited_assessment = st.text_area("Assessment", value=st.session_state.current_note["assessment"])
    edited_plan = st.text_area("Plan", value=st.session_state.current_note["plan"])
    # Each text_area is pre-filled (value=...) with the AI's draft, but the user can type over it.
    # Whatever the user currently sees in each box is automatically the latest value of these variables.

    if st.button("Save Note"):
        notes = load_notes()  
        # Load whatever notes already exist on disk first, so we don't overwrite past ones.

        notes.append({  
            # .append() adds a new entry to the end of our list.
            "timestamp": str(datetime.datetime.now()),  
            # Records exactly when this note was saved.
            "subjective": edited_subjective,
            "objective": edited_objective,
            "assessment": edited_assessment,
            "plan": edited_plan
        })

        save_notes(notes)  
        # Writes the updated full list (old notes + this new one) back to notes.json.
        st.success("Note saved!")  
        # st.success() shows a green confirmation message.

st.divider()  
# Draws a horizontal line to visually separate the new-note section from saved notes below.

st.subheader("Past Saved Notes")
all_notes = load_notes()

if len(all_notes) == 0:
    st.write("No notes saved yet.")
else:
    for n in reversed(all_notes):  
        # reversed() shows the most recently saved note first instead of oldest-first.
        with st.expander(f"Note from {n['timestamp']}"):  
            # st.expander() creates a collapsible section — keeps the page tidy when there are many notes.
            st.write("**Subjective:**", n["subjective"])
            st.write("**Objective:**", n["objective"])
            st.write("**Assessment:**", n["assessment"])
            st.write("**Plan:**", n["plan"])