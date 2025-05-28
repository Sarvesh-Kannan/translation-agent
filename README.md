# Hybrid Translation Service

A powerful translation service that combines Translation Memory (TM) with Sarvam AI's translation API to provide efficient and accurate translations for Indian languages.

## Features

### Translation Capabilities
- Hybrid translation approach combining TM and Sarvam AI API
- Support for multiple Indian languages:
  - English (en-IN)
  - Hindi (hi-IN)
  - Bengali (bn-IN)
  - Gujarati (gu-IN)
  - Kannada (kn-IN)
  - Malayalam (ml-IN)
  - Marathi (mr-IN)
  - Odia (od-IN)
  - Punjabi (pa-IN)
  - Tamil (ta-IN)
  - Telugu (te-IN)

### Translation Memory (TM)
- Efficient storage and retrieval of translations
- Fuzzy matching for similar text segments
- TMX file import/export support
- Segment-level translation storage
- Automatic learning from new translations

### Translation Modes
- Formal
- Modern Colloquial
- Classic Colloquial

### Output Scripts
- Default script
- Roman script
- Fully native script
- Spoken form in native script

### Domain Support
- General
- Technical
- Medical
- Legal
- Marketing

## Technical Implementation

### Hybrid Translation Process
1. Text Segmentation
   - Splits input text into meaningful chunks
   - Uses NLTK for intelligent sentence segmentation
   - Preserves context and formatting

2. Translation Memory Lookup
   - Searches for exact and fuzzy matches in TM
   - Uses confidence scoring for match quality
   - Maintains translation consistency

3. Sarvam AI Integration
   - Falls back to API for unknown segments
   - Optimizes API usage by combining requests
   - Automatic storage of new translations

4. Result Reconstruction
   - Intelligent merging of TM and API translations
   - Preserves original formatting
   - Provides translation statistics

## Setup

1. Install Dependencies:
```bash
pip install -r requirements.txt
```

2. Required Python packages:
- fastapi==0.104.1
- uvicorn==0.24.0
- streamlit==1.29.0
- nltk==3.8.1
- requests==2.31.0
- (and other dependencies listed in requirements.txt)

3. Environment Configuration:
- Set up Sarvam AI API key
- Configure TM storage location
- Set default language pairs

## Usage

### Running the Application
```bash
streamlit run app/streamlit_app.py
```

### Web Interface Features
1. Translation
   - Input text area
   - Language selection
   - Translation mode options
   - Script selection
   - Domain selection

2. Translation Memory Management
   - TMX file import/export
   - Statistics view
   - Memory cleanup tools

3. Analytics
   - Translation source tracking (TM vs API)
   - Confidence scores
   - Performance metrics

## Project Structure
```
.
├── app/
│   ├── streamlit_app.py    # Main Streamlit application
│   ├── utils/              # Utility functions
│   └── data/              # Configuration and data files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Performance Features
- Efficient chunk-based translation
- Parallel processing where possible
- Optimized API usage
- Continuous learning system
- Translation memory management

## Future Improvements
- Enhanced fuzzy matching algorithms
- More language pair support
- Advanced domain adaptation
- Machine learning for match prediction
- API load balancing
- Extended TMX format support



So as in for making the upadted version of the same rather than just sticking on to the Sarvam API, it can be extended as an hybrid approach by incorporating both of the API and the Translation Memory together so that the Sarvam API, can act as a fallback mechanism to the words that are not present in the Translation memory. So, then the workflow would be like the word which is supposedly is to be translated into the desired language first the model shall perform some similarity check task in the existing translation memory and then upon checking in that if the exact words or rather the splits of a large paragraph is being set in there it shall return  the translated verrsion of the original text which had been inputted by the user, but if it is not present in the knowledge base which is the database in which the translation memory is present in it shall then access the Sarvam API for the translation which can provide with the real time translation for any of the resources the user inputs in their desired language. By doing this it can be scaled up to a bigger level and can be used very well in industries as well, which makes this approach the penultimate task for the corporates to stick on with. 
