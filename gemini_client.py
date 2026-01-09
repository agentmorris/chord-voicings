import os
import json
from google import genai
from google.genai import types

# Configuration
API_KEY_PATH = r"g:\temp\gemini_key.txt"
MODEL_NAME = "gemini-3-pro-preview" 

def get_api_key():
    try:
        with open(API_KEY_PATH, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def get_voicings(challenge, chord_data):
    """
    Asks Gemini for voicings for a list of chords based on a challenge.
    
    Args:
        challenge (str): The specific challenge description.
        chord_data (list): List of dicts, e.g., [{'row': 0, 'chord': 'G'}, ...]
        
    Returns:
        list: List of dicts with 'row', 'chord_display_name', 'fingering', 'starting_fret'.
    """
    api_key = get_api_key()
    if not api_key:
        return []
        
    client = genai.Client(api_key=api_key)
    
    # Construct the prompt
    # We want a JSON response.
    prompt = f"""
    You are an expert guitar instructor.
    
    Challenge: "{challenge}"
    
    Here is the sequence of chords in a song, organized by row (line number):
    {json.dumps(chord_data)}
    
    Please provide a specific guitar voicing for each chord in the sequence that satisfies the challenge.
    Return the result strictly as a JSON list of objects.
    
    Each object must have:
    - "row": The integer row index corresponding to the input chord.
    - "chord_display_name": The name of the chord to display. This can be different from the input chord (e.g. if the challenge is to add extensions, input "G" might become "Gmaj9").
    - "fingering": A string of 6 numbers or 'x' separated by spaces, representing frets from Low E (6th string) to High e (1st string). Use 'x' for muted strings and '0' for open strings.
    - "starting_fret": An integer indicating the fret number of the lowest displayed fret in the diagram (usually 1, unless playing high up the neck).
    
    Important rules:
    1. You may return more chords than provided if the challenge implies insertion (e.g. secondary dominants). Ensure they have the correct "row" index.
    2. You may return fewer chords if the challenge implies simplification.
    3. The "row" index is crucial for placing the chord correctly in the lyrics.
    
    If a chord is repeated many times and the challenge implies keeping the same voicing, simply repeat the voicing object.
    If the challenge suggests "skipping" a chord (e.g. for a sparse arrangement), you can simply omit it from the list, or return it with "fingering": "SKIP".
    
    Do not include markdown formatting (like ```json) in the response, just the raw JSON string.
    """
    
    try:
        print(f"Sending request to {MODEL_NAME} for {len(chord_data)} chords...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        text = response.text
        if not text:
             return []
        text = text.strip()
        # Clean potential markdown code blocks if the model ignores the instruction
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text)
        return data
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return []

if __name__ == "__main__":
    # Test
    chords = [
        {"row": 0, "chord": "G"}, 
        {"row": 0, "chord": "C/G"}, 
        {"row": 1, "chord": "G"}, 
        {"row": 1, "chord": "D"}
    ]
    challenge = "Convert all major triads to major 9th chords"
    result = get_voicings(challenge, chords)
    print(json.dumps(result, indent=2))
