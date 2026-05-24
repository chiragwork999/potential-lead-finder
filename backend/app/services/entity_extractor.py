from __future__ import annotations

import spacy

_NLP = None


import spacy

_NLP = None


def _get_nlp():
    global _NLP

    if _NLP is None:
        try:
            _NLP = spacy.load("en_core_web_sm")
        except Exception as e:
            print("SpaCy model not found:", e)
            return None

    return _NLP


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        cleaned = value.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            output.append(cleaned)
    return output


def extract_entities(text: str) -> dict:
    if not text:
        return {
            "organizations": [],
            "people": [],
            "locations": [],
            "money": [],
            "dates": [],
        }

    nlp = _get_nlp()

    if nlp is None:
        return {
            "organizations": [],
            "locations": [],
            "money": [],
        }

    doc = nlp(text)
    entities = {
        "organizations": [],
        "people": [],
        "locations": [],
        "money": [],
        "dates": [],
    }

    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ == "PERSON":
            entities["people"].append(ent.text)
        elif ent.label_ == "GPE":
            entities["locations"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)

    for key in entities:
        entities[key] = _dedupe(entities[key])

    return entities
