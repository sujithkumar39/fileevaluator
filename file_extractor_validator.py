import streamlit as st
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyC0wO5NZgJ1W1Hbz_szEblGikA7mBcUzS0")  # Replace with your real Gemini API key

def extract_text_from_image(image_file):
    model = genai.GenerativeModel("gemini-1.5-flash")
    image_bytes = image_file.getvalue()

    try:
        response = model.generate_content([
            "Extract all visible content from this image (text, formulas, notes, etc.) as clearly as possible.",
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def validate_information(extracted_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an expert tutor.
    Review the following extracted content from a handwritten image:
    {extracted_text}
    Your task:
    - Identify any incorrect facts or formulas.
    - Correct them.
    - Show all possible correct variations.
    - Explain the correct concept clearly as a tutor would to a student.
    Use a friendly tone, and keep your explanations simple and clear.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def calculate_score(extracted, validation):
    # Simple example of scoring based on content length, adjust as necessary
    content_score = min(len(extracted) / 5, 40)
    validation_score = min(len(validation) / 10, 40)
    explanation_score = 20 if "explanation" in validation.lower() else 10
    total_score = content_score + validation_score + explanation_score
    grade = "A" if total_score >= 90 else "B" if total_score >= 70 else "C"
    return round(total_score, 2), grade

# --- Streamlit UI ---
st.set_page_config(page_title="Image Data Extractor and Validator", layout="centered")

st.title("Extracts and Validats the image")
st.markdown("""Upload your handwritten or any image with content such as formulas, definitions, or notes.
The AI will validate and explain the content like a tutor.""")

st.subheader("Upload Your Handwritten Image")
uploaded_image = st.file_uploader("Upload a JPG, JPEG, or PNG file", type=["jpg", "jpeg", "png"])

if uploaded_image:
    try:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image Preview", use_container_width=True)

        with st.spinner("Processing image content..."):
            extracted = extract_text_from_image(uploaded_image)
            validation = validate_information(extracted)
            score, grade = calculate_score(extracted, validation)

        st.subheader("Extracted Data:")
        st.code(extracted)

        st.subheader("Tutor Explanation and Corrections:")
        st.markdown(validation)

        st.subheader("Score and Grade:")
        st.markdown(f"Your score for this extraction and validation is: **{score}/100**")
        st.markdown(f"Grade: **{grade}**")

    except UnidentifiedImageError:
        st.error("Invalid image. Please upload a valid JPG, JPEG, or PNG.")
    except Exception as e:
        st.error(f"Error processing image: {e}")
        