import streamlit as st
import requests
import json
from utils.translation_memory import TranslationMemory
from utils.glossary import Glossary

# Set page config first
st.set_page_config(page_title="Advanced Translation Service", page_icon="🌐")

# Sarvam AI API Configuration
SARVAM_API_ENDPOINT = "https://api.sarvam.ai/translate"
API_KEY = "b61ffcf0-9e8f-498e-bb5d-4b7f8eb70132"

# Initialize Translation Memory and Glossary
@st.cache_resource
def get_tm():
    return TranslationMemory()

@st.cache_resource
def get_glossary():
    return Glossary()

tm = get_tm()
glossary = get_glossary()

# Supported languages (as per Sarvam AI documentation)
LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "od-IN": "Odia",
    "pa-IN": "Punjabi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu"
}

def translate_text(text, source_lang, target_lang, translation_mode="formal", 
                  output_script=None, domain=None):
    """Translate text using TM, Glossary, and Sarvam AI API"""
    
    # Step 1: Check Translation Memory for exact or fuzzy matches
    tm_match = tm.find_match(text, source_lang, target_lang, threshold=0.8)
    if tm_match:
        translation, similarity = tm_match
        st.info(f"Found TM match with {similarity*100:.1f}% similarity")
        return translation
    
    # Step 2: Use Sarvam AI API for translation
    headers = {
        "api-subscription-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": target_lang,
        "mode": translation_mode
    }
    
    if output_script and output_script != "Default":
        payload["output_script"] = output_script.lower()
    
    try:
        response = requests.post(SARVAM_API_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            translation = result["translated_text"]
            
            # Step 3: Apply glossary terms to the translation
            if domain:
                translation = glossary.apply_glossary(
                    translation, source_lang, target_lang, domain
                )
            
            # Step 4: Store the translation in TM
            tm.add_translation(text, translation, source_lang, target_lang)
            
            return translation
        else:
            st.error(f"API Error: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        return None

# Streamlit UI
st.title("🌐 Advanced Translation Service")
st.write("Powered by Sarvam AI with TM and Glossary Support")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["Translate", "Translation Memory", "Glossary"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox(
            "Translate from:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key="source_lang"
        )

    with col2:
        target_lang = st.selectbox(
            "Translate to:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key="target_lang"
        )

    # Text input
    text_input = st.text_area("Enter text to translate:", height=150)

    # Translation options
    with st.expander("Translation Options"):
        col3, col4 = st.columns(2)
        
        with col3:
            translation_mode = st.selectbox(
                "Translation Mode:",
                options=["formal", "modern-colloquial", "classic-colloquial"],
                help="Select the tone or style of translation"
            )
            
            output_script = st.selectbox(
                "Output Script:",
                options=["Default", "roman", "fully-native", "spoken-form-in-native"],
                help="Select the desired script format for the output"
            )
            
        with col4:
            domain = st.selectbox(
                "Domain:",
                options=["general"] + glossary.get_domains(),
                help="Select the domain for terminology"
            )

    # Translate button
    if st.button("Translate"):
        if not API_KEY:
            st.error("Please set your Sarvam AI API key in the code.")
        elif text_input:
            with st.spinner("Translating..."):
                try:
                    translation = translate_text(
                        text_input,
                        source_lang,
                        target_lang,
                        translation_mode,
                        output_script,
                        domain
                    )
                    
                    if translation:
                        st.success("Translation Complete!")
                        st.write("### Translation:")
                        st.info(translation)
                        
                        # Show source text for reference
                        st.write("### Original Text:")
                        st.text(text_input)
                    
                except Exception as e:
                    st.error(f"Translation failed: {str(e)}")
        else:
            st.warning("Please enter some text to translate.")

with tab2:
    st.header("Translation Memory Management")
    
    # TM Statistics
    stats = tm.get_statistics()
    st.write("### Statistics")
    col5, col6, col7 = st.columns(3)
    col5.metric("Total Translation Pairs", stats["total_pairs"])
    col6.metric("Source Languages", len(stats["source_languages"]))
    col7.metric("Target Languages", len(stats["target_languages"]))
    
    # TMX Import/Export
    st.write("### Import/Export TMX")
    col8, col9 = st.columns(2)
    
    with col8:
        tmx_file = st.file_uploader("Import TMX File", type=["tmx"])
        if tmx_file and st.button("Import TMX"):
            try:
                tm.import_tmx(tmx_file)
                st.success("TMX file imported successfully!")
            except Exception as e:
                st.error(f"Failed to import TMX: {str(e)}")
    
    with col9:
        if st.button("Export TMX"):
            try:
                export_path = "app/data/tm/export.tmx"
                tm.export_tmx(export_path)
                st.success(f"TMX exported to {export_path}")
            except Exception as e:
                st.error(f"Failed to export TMX: {str(e)}")

with tab3:
    st.header("Glossary Management")
    
    # Add new term
    with st.expander("Add New Term"):
        col10, col11 = st.columns(2)
        
        with col10:
            source_term = st.text_input("Source Term")
            source_lang_term = st.selectbox(
                "Source Language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                key="source_lang_term"
            )
        
        with col11:
            target_term = st.text_input("Target Term")
            target_lang_term = st.selectbox(
                "Target Language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                key="target_lang_term"
            )
        
        term_domain = st.text_input("Domain", value="general")
        term_context = st.text_area("Context (Optional)")
        
        if st.button("Add Term"):
            if source_term and target_term:
                glossary.add_term(
                    source_term,
                    target_term,
                    source_lang_term,
                    target_lang_term,
                    term_domain,
                    term_context
                )
                st.success("Term added successfully!")
            else:
                st.warning("Please enter both source and target terms.")
    
    # Import/Export Glossary
    st.write("### Import/Export Glossary")
    col12, col13 = st.columns(2)
    
    with col12:
        glossary_file = st.file_uploader("Import Glossary (CSV)", type=["csv"])
        if glossary_file and st.button("Import Glossary"):
            try:
                glossary.import_glossary(glossary_file)
                st.success("Glossary imported successfully!")
            except Exception as e:
                st.error(f"Failed to import glossary: {str(e)}")
    
    with col13:
        if st.button("Export Glossary"):
            try:
                export_path = "app/data/glossaries/export.csv"
                glossary.export_glossary(export_path)
                st.success(f"Glossary exported to {export_path}")
            except Exception as e:
                st.error(f"Failed to export glossary: {str(e)}") 