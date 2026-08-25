# Hitahara
A full-stack health-tech application that leverages Optical Character Recognition (OCR) and Natural Language Processing (NLP) to parse semi-structured food ingredient labels. The backend utilizes an optimized fuzzy-matching algorithm to map obscure chemical synonyms directly to primary allergens and chronic disease contraindications.

Project Scope: A multimodal health-tech system combining Document OCR, Fuzzy Matching NLP, and Computer Vision to deliver personalized dietary risk assessments.

Document AI Pipeline: Ingests unstructured diagnostic lab reports to extract metabolic biomarkers (e.g., HbA1c, triglycerides, serum ferritin) and normalizes them into a structured metabolic profile.

Dynamic Food Parsing Engine: Processes packaged food ingredient lists using OCR, cross-referencing extracted additives against the user's biomarker profile via an optimized mapping dictionary.

Quantitative Tolerance Scoring: Calculates compound-level thresholds, moving beyond binary alerts to provide personalized safety scores and actionable consumption guidance.
