import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple
import os
import json
from datetime import datetime
import difflib

class TranslationMemory:
    def __init__(self, tm_dir: str = "app/data/tm"):
        self.tm_dir = tm_dir
        self.memory: Dict[str, Dict[str, dict]] = {}
        self.initialize_tm()

    def initialize_tm(self):
        """Initialize translation memory from stored files"""
        os.makedirs(self.tm_dir, exist_ok=True)
        
        # Load JSON TM if exists
        json_path = os.path.join(self.tm_dir, "translation_memory.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)

    def save_tm(self):
        """Save translation memory to JSON file"""
        json_path = os.path.join(self.tm_dir, "translation_memory.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def import_tmx(self, tmx_file: str):
        """Import translations from TMX file"""
        tree = ET.parse(tmx_file)
        root = tree.getroot()
        
        for tu in root.findall(".//tu"):
            source_lang = None
            target_lang = None
            source_text = None
            target_text = None
            
            for tuv in tu.findall("tuv"):
                lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
                seg = tuv.find("seg")
                
                if seg is not None:
                    if source_lang is None:
                        source_lang = lang
                        source_text = seg.text
                    else:
                        target_lang = lang
                        target_text = seg.text
            
            if source_text and target_text and source_lang and target_lang:
                self.add_translation(
                    source_text,
                    target_text,
                    source_lang,
                    target_lang
                )

    def export_tmx(self, output_file: str):
        """Export translations to TMX file"""
        root = ET.Element("tmx", version="1.4")
        header = ET.SubElement(root, "header", 
                             creationdate=datetime.now().strftime("%Y%m%dT%H%M%S"),
                             srclang="en-IN")
        body = ET.SubElement(root, "body")

        for src_lang, translations in self.memory.items():
            for tgt_lang, pairs in translations.items():
                for source, target in pairs.items():
                    tu = ET.SubElement(body, "tu")
                    
                    # Source
                    tuv_src = ET.SubElement(tu, "tuv", {"xml:lang": src_lang})
                    seg_src = ET.SubElement(tuv_src, "seg")
                    seg_src.text = source
                    
                    # Target
                    tuv_tgt = ET.SubElement(tu, "tuv", {"xml:lang": tgt_lang})
                    seg_tgt = ET.SubElement(tuv_tgt, "seg")
                    seg_tgt.text = target["text"]

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

    def add_translation(self, source_text: str, target_text: str, 
                       source_lang: str, target_lang: str, context: str = None):
        """Add a translation pair to the memory"""
        if source_lang not in self.memory:
            self.memory[source_lang] = {}
        
        if target_lang not in self.memory[source_lang]:
            self.memory[source_lang][target_lang] = {}
        
        self.memory[source_lang][target_lang][source_text] = {
            "text": target_text,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.save_tm()

    def find_match(self, source_text: str, source_lang: str, 
                  target_lang: str, threshold: float = 0.8) -> Optional[Tuple[str, float]]:
        """Find the best matching translation from memory"""
        if source_lang not in self.memory or target_lang not in self.memory[source_lang]:
            return None

        best_match = None
        best_ratio = 0

        for stored_source, translation in self.memory[source_lang][target_lang].items():
            ratio = difflib.SequenceMatcher(None, source_text.lower(), 
                                          stored_source.lower()).ratio()
            
            if ratio > threshold and ratio > best_ratio:
                best_ratio = ratio
                best_match = translation["text"]

        return (best_match, best_ratio) if best_match else None

    def get_statistics(self) -> dict:
        """Get statistics about the translation memory"""
        stats = {
            "total_pairs": 0,
            "language_pairs": [],
            "source_languages": set(),
            "target_languages": set()
        }
        
        for src_lang, translations in self.memory.items():
            stats["source_languages"].add(src_lang)
            for tgt_lang, pairs in translations.items():
                stats["target_languages"].add(tgt_lang)
                stats["total_pairs"] += len(pairs)
                stats["language_pairs"].append(f"{src_lang}->{tgt_lang}")
        
        stats["source_languages"] = list(stats["source_languages"])
        stats["target_languages"] = list(stats["target_languages"])
        return stats 