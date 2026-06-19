import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st  
# Streamlit's convention is always to import it "as st" — you'll see this in every Streamlit app.

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

st.title("Clinical Scribe Assistant")  
# st.title() renders a big heading at the top of the web page.

st.write("Paste a doctor-patient conversation below to generate a SOAP note.")  
# st.write() displays plain text/instructions on the page.

conversation = st.text_area("Conversation", height=250)  
# st.text_area() creates a big multi-line text box on the page.
# Whatever the user types/pastes gets stored in the "conversation" variable.
# "Conversation" is the label shown above the box; height=250 sets its size in pixels.

if st.button("Generate SOAP Note"):  
    # st.button() draws a clickable button. This code only runs when it's clicked —
    # that's what the "if" does here: "if the button was just clicked, do the following."

    if conversation.strip() == "":  
        # .strip() removes extra blank spaces; this checks if the box was left empty.
        st.warning("Please paste a conversation first.")  
        # st.warning() shows a yellow warning message on the page.
    else:
        with st.spinner("Generating note..."):  
            # st.spinner() shows a little loading animation while the code inside runs —
            # useful feedback since the AI call takes a few seconds.

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
                )
            )

            note = json.loads(response.text)

        st.subheader("Subjective")  
        # st.subheader() makes a smaller heading, one for each SOAP section.
        st.write(note["subjective"])

        st.subheader("Objective")
        st.write(note["objective"])

        st.subheader("Assessment")
        st.write(note["assessment"])

        st.subheader("Plan")
        st.write(note["plan"])