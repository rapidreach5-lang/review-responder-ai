import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ReviewResponse(BaseModel):
    sentiment: str = Field(description="Θετική, Ουδέτερη ή Αρνητική")
    key_points: list[str] = Field(description="Τα 2-3 βασικά σημεία που αναφέρει ο πελάτης")
    friendly_reply: str = Field(description="Ζεστή, φιλική απάντηση εκ μέρους της επιχείρησης")
    professional_reply: str = Field(description="Πιο τυπική και επαγγελματική απάντηση")


st.set_page_config(page_title="AI Review Responder", page_icon="⭐")
st.title("⭐ AI Review Responder για Επιχειρήσεις")
st.write("Επικόλλησε μια κριτική πελάτη και πάρε έτοιμες, επαγγελματικές απαντήσεις.")

business_name = st.text_input("Όνομα Επιχείρησης", value="Coffee Lab")

col1, col2 = st.columns(2)
with col1:
    business_type = st.selectbox(
        "Είδος Επιχείρησης",
        ["Καφέ / Εστίαση", "Γυμναστήριο", "Κατάστημα Λιανικής", "Άλλο"],
    )
with col2:
    reply_language = st.selectbox(
        "Γλώσσα Απάντησης",
        ["Ελληνικά", "Αγγλικά"],
    )

review_text = st.text_area(
    "Κριτική Πελάτη",
    placeholder="Π.χ. Πολύ ωραίος καφές, αλλά περιμέναμε 20 λεπτά να εξυπηρετηθούμε...",
)

if st.button("Δημιουργία Απαντήσεων", type="primary"):
    if not review_text.strip():
        st.warning("Γράψε ή επικόλλησε πρώτα μια κριτική.")
    else:
        with st.spinner("Αναλύεται η κριτική..."):
            prompt = f"""
            Είσαι ειδικός εξυπηρέτησης πελατών για την επιχείρηση '{business_name}' ({business_type}).
            Ανάλυσε την παρακάτω κριτική πελάτη και γράψε δύο απαντήσεις στη γλώσσα: {reply_language}.
            (Τα πεδία sentiment και key_points κράτησέ τα στα Ελληνικά ώστε να τα διαβάζει εύκολα ο ιδιοκτήτης/υπεύθυνος.)
            Αν η κριτική είναι αρνητική, κράτα ψύχραιμο, ευγενικό ύφος, αναγνώρισε το πρόβλημα χωρίς δικαιολογίες και κάλεσε τον πελάτη να ξανάρθει.

            Κριτική:
            {review_text}
            """

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ReviewResponse,
                },
            )

            result = ReviewResponse.model_validate_json(response.text)

            st.subheader(f"Αίσθημα Κριτικής: {result.sentiment}")
            st.markdown("**Βασικά σημεία πελάτη:**")
            for point in result.key_points:
                st.write(f"- {point}")

            st.divider()
            st.subheader(f"😊 Φιλική Απάντηση ({reply_language})")
            st.info(result.friendly_reply)

            st.subheader(f"👔 Επαγγελματική / Τυπική Απάντηση ({reply_language})")
            st.success(result.professional_reply)