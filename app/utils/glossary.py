import json
import os
from typing import Dict, List, Optional

class Glossary:
    def __init__(self, glossary_dir: str = "app/data/glossaries"):
        self.glossary_dir = glossary_dir
        self.terms: Dict[str, Dict[str, dict]] = {}
        self.initialize_glossary()

    def initialize_glossary(self):
        """Initialize glossary from stored files"""
        os.makedirs(self.glossary_dir, exist_ok=True)
        
        # Load JSON glossary if exists
        json_path = os.path.join(self.glossary_dir, "glossary.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                self.terms = json.load(f)

    def save_glossary(self):
        """Save glossary to JSON file"""
        json_path = os.path.join(self.glossary_dir, "glossary.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.terms, f, ensure_ascii=False, indent=2)

    def add_term(self, source_term: str, target_term: str, 
                source_lang: str, target_lang: str, 
                domain: str = "general", context: str = None):
        """Add a term to the glossary"""
        if source_lang not in self.terms:
            self.terms[source_lang] = {}
        
        if target_lang not in self.terms[source_lang]:
            self.terms[source_lang][target_lang] = {}
        
        self.terms[source_lang][target_lang][source_term.lower()] = {
            "term": target_term,
            "domain": domain,
            "context": context
        }
        self.save_glossary()

    def get_term(self, source_term: str, source_lang: str, 
                target_lang: str, domain: str = None) -> Optional[str]:
        """Get translation for a term from the glossary"""
        if (source_lang in self.terms and 
            target_lang in self.terms[source_lang] and 
            source_term.lower() in self.terms[source_lang][target_lang]):
            
            term_entry = self.terms[source_lang][target_lang][source_term.lower()]
            if domain is None or term_entry["domain"] == domain:
                return term_entry["term"]
        return None

    def import_glossary(self, file_input, format: str = "csv"):
        """Import terms from a file (CSV or TBX format)
        Args:
            file_input: Either a file path string or a file-like object (e.g. Streamlit UploadedFile)
            format: The format of the file ('csv' or 'tbx')
        """
        if format == "csv":
            # Handle both string paths and file-like objects
            if isinstance(file_input, str):
                f = open(file_input, 'r', encoding='utf-8')
            else:
                # For file-like objects (e.g. Streamlit's UploadedFile)
                f = file_input
                
            try:
                # Skip header row
                next(f)
                for line in f:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8')
                    parts = line.strip().split(',')
                    if len(parts) >= 4:  # source_term,target_term,source_lang,target_lang[,domain[,context]]
                        source_term, target_term, source_lang, target_lang = parts[:4]
                        domain = parts[4] if len(parts) > 4 else "general"
                        context = parts[5] if len(parts) > 5 else None
                        self.add_term(source_term, target_term, source_lang, 
                                    target_lang, domain, context)
            finally:
                # Only close if it's a file we opened
                if isinstance(file_input, str):
                    f.close()

    def export_glossary(self, file_path: str, format: str = "csv"):
        """Export terms to a file (CSV or TBX format)"""
        if format == "csv":
            with open(file_path, 'w', encoding='utf-8') as f:
                for src_lang, translations in self.terms.items():
                    for tgt_lang, terms in translations.items():
                        for src_term, entry in terms.items():
                            line = f"{src_term},{entry['term']},{src_lang},{tgt_lang}"
                            line += f",{entry['domain']}"
                            if entry.get('context'):
                                line += f",{entry['context']}"
                            f.write(line + "\n")

    def get_domains(self) -> List[str]:
        """Get list of all domains in the glossary"""
        domains = set()
        for src_lang in self.terms.values():
            for tgt_lang in src_lang.values():
                for term in tgt_lang.values():
                    domains.add(term["domain"])
        return list(domains)

    def apply_glossary(self, text: str, source_lang: str, 
                      target_lang: str, domain: str = None) -> str:
        """Apply glossary terms to a text"""
        if source_lang not in self.terms or target_lang not in self.terms[source_lang]:
            return text
            
        result = text
        # Sort terms by length (longest first) to handle compound terms correctly
        terms = sorted(self.terms[source_lang][target_lang].keys(), 
                      key=len, reverse=True)
        
        for term in terms:
            if term in text.lower():
                translation = self.get_term(term, source_lang, target_lang, domain)
                if translation:
                    # Case-sensitive replacement
                    result = result.replace(term, translation)
                    result = result.replace(term.capitalize(), translation.capitalize())
        
        return result 