import re
from typing import List, Dict

def extract_clauses(text: str) -> List[Dict[str, str]]:
    """
    Identifies BIS clause markers from document text such as:
    - 'Clause 3.1 Materials'
    - '4.2.1 Sampling and Criteria for Conformity'
    - '5. Requirements'
    - 'Table 1 - Chemical Requirements'
    """
    clauses = []
    
    # Regex patterns for BIS clauses
    clause_patterns = [
        r'(?:CLAUSE\s+)?(\b\d+(?:\.\d+)+\b)\s+([^\n\r]{3,80})',
        r'(\b\d+\b)\s+([A-Z\s]{4,60})(?=\n|\r)',
        r'(Table\s+\d+[\w\s\-]*)'
    ]
    
    for pattern in clause_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            if len(m.groups()) == 2:
                c_num = m.group(1).strip()
                c_title = m.group(2).strip()
                clauses.append({
                    "clause_number": c_num,
                    "clause_title": c_title
                })
            elif len(m.groups()) == 1:
                clauses.append({
                    "clause_number": m.group(1).strip(),
                    "clause_title": "Table / Schedule"
                })

    # Return deduplicated clauses preserving order
    seen = set()
    deduped = []
    for c in clauses:
        key = c["clause_number"]
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return deduped
