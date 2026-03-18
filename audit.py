import re

def audit_summary(summary_text):
    """
    Checks for loaded language or non-neutral terms.
    This mimics the Phase 4 Agent D Audit Pass.
    """
    loaded_words = [
        "outrageous", "shocking", "common sense", "everyone knows",
        "radical", "extremist", "heroic", "villainous", "failed",
        "masterpiece", "disaster", "slammed", "blasted", "eviscerated"
    ]
    
    findings = []
    for word in loaded_words:
        if re.search(rf"\b{word}\b", summary_text, re.IGNORECASE):
            findings.append(word)
            
    return findings

if __name__ == "__main__":
    test_text = "The policy was a total disaster and the politician was slammed by the public."
    print(f"Audit Results: {audit_summary(test_text)}")
