from typing import Dict, List, Any

# Regulatory Concept Taxonomy for Bureau of Indian Standards
REGULATORY_TAXONOMY = {
    "drinking_water": {
        "standard": "IS 10500:2012",
        "title": "Drinking Water — Specification",
        "material": "Potable Water",
        "industry": "Food & Beverage",
        "scheme": "Scheme-I (ISI Mark)",
        "testing": "Microbiological and Chemical Parameter Test",
        "lab": "BIS Central Laboratory, Sahibabad",
        "rule": "Bureau of Indian Standards (Conformity Assessment) Regulations, 2018"
    },
    "packaged_drinking_water": {
        "standard": "IS 14543:2018",
        "title": "Packaged Drinking Water (Other than Packaged Natural Mineral Water)",
        "material": "Treated Water",
        "industry": "Food & Beverage",
        "scheme": "Scheme-I (Mandatory ISI Mark)",
        "testing": "Pesticide Residue and Heavy Metal Analysis",
        "lab": "National Accreditation Board for Testing and Calibration Laboratories (NABL)",
        "rule": "Food Safety and Standards (Packaging) Regulations & BIS Act 2016"
    },
    "cement": {
        "standard": "IS 12269:2013",
        "title": "Ordinary Portland Cement, 53 Grade — Specification",
        "material": "Clinker, Gypsum",
        "industry": "Civil & Construction",
        "scheme": "Scheme-I (Mandatory Certification)",
        "testing": "Compressive Strength & Setting Time Test",
        "lab": "National Council for Cement and Building Materials (NCCBM)",
        "rule": "Cement (Quality Control) Order"
    },
    "helmets": {
        "standard": "IS 4151:2015",
        "title": "Protective Helmets for Two Wheeler Riders",
        "material": "Thermoplastic / Composite Fiber",
        "industry": "Automotive Safety",
        "scheme": "Scheme-I (Mandatory ISI Mark)",
        "testing": "Impact Absorption and Retention Test",
        "lab": "Automotive Research Association of India (ARAI)",
        "rule": "Central Motor Vehicles Rules (CMVR)"
    },
    "steel_bars": {
        "standard": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
        "material": "Carbon Steel",
        "industry": "Metallurgy & Construction",
        "scheme": "Scheme-I (Mandatory Certification)",
        "testing": "Tensile Strength and Bend Testing",
        "lab": "National Metallurgical Laboratory (NML)",
        "rule": "Steel and Steel Products (Quality Control) Order"
    }
}

class RegulatoryMapper:
    """
    Maps user entities, products, and intents to official BIS regulatory taxonomy concepts.
    """
    def map_to_concepts(self, product_terms: List[str], detected_standards: List[str]) -> List[Dict[str, Any]]:
        mapped_concepts = []
        
        # Check standard matches
        for std in detected_standards:
            std_clean = std.upper().replace(" ", "")
            for key, data in REGULATORY_TAXONOMY.items():
                if data["standard"].upper().replace(" ", "") in std_clean or std_clean in data["standard"].upper().replace(" ", ""):
                    mapped_concepts.append(data)

        # Check product term matches
        for term in product_terms:
            t = term.lower()
            for key, data in REGULATORY_TAXONOMY.items():
                if t in key or any(t in word.lower() for word in data["title"].split()):
                    if data not in mapped_concepts:
                        mapped_concepts.append(data)

        return mapped_concepts
