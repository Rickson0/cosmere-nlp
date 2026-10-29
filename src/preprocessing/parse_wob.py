import re

def strip_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("*", "").replace("&quot;", '"').replace("&amp;", "&")
    return text.strip()

def extract_brandon_text(wob):
    parts = [
        strip_html(line["text"])
        for line in wob.get("lines", [])
        if line.get("speaker") == "Brandon Sanderson"
    ]
    return " ".join(parts)
def extract_question_text(wob):
    parts = [
        strip_html(line["text"])
        for line in wob.get("lines", [])
        if not line.get("speaker", "").lower().startswith("brandon")
    ]
    return " ".join(parts)

def extract_full_text(wob):
    return " ".join(strip_html(line["text"]) for line in wob.get("lines", []))
    
RESPONDERS = {
    "brandon sanderson",
    "peter ahlstrom",
    "isaac stewart",
    
    
}

def extract_answer_text(wob):
    parts = []
    for line in wob.get("lines", []):
        speaker = line.get("speaker", "").lower().strip()
        if speaker in RESPONDERS:
            parts.append(strip_html(line["text"]))
    return " ".join(parts)

