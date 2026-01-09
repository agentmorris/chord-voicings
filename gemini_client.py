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

def get_voicings(challenge, chord_list):
    """
    Asks Gemini for voicings for a list of chords based on a challenge.
    
    Args:
        challenge (str): The specific challenge description.
        chord_list (list): List of chord names in order.
        
    Returns:
        list: List of dicts with 'chord', 'fingering', 'starting_fret'.
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
    
    Here is the sequence of chords in a song:
    {json.dumps(chord_list)}
    
    Please provide a specific guitar voicing for each chord in the sequence that satisfies the challenge.
    Return the result strictly as a JSON list of objects.
    
    Each object must have:
    - "chord": The name of the chord (as provided).
    - "fingering": A string of 6 numbers or 'x' separated by spaces, representing frets from Low E (6th string) to High e (1st string). Use 'x' for muted strings and '0' for open strings.
    - "starting_fret": An integer indicating the fret number of the lowest displayed fret in the diagram (usually 1, unless playing high up the neck).
    
    If a chord is repeated many times and the challenge implies keeping the same voicing, simply repeat the voicing object.
    If the challenge suggests "skipping" a chord (e.g. for a sparse arrangement), use "SKIP" as the fingering.
    
    Do not include markdown formatting (like ```json) in the response, just the raw JSON string.
    """
    
    try:
        print(f"Sending request to {MODEL_NAME} for {len(chord_list)} chords...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        text = response.text.strip()
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
    chords = ["G", "C/G", "G", "D"]
    challenge = "Play all chords as triads using on the 2nd, 3rd, and 5th strings"
    result = get_voicings(challenge, chords)
    print(json.dumps(result, indent=2))
