import os
from google import genai
from google.genai import types

# Configuration
API_KEY_PATH = r"g:\temp\gemini_key.txt"
OUTPUT_FILE = "challenges.txt"
MODEL_TAG_REQUESTED = "gemini-3-pro-preview"
FALLBACK_MODELS = []

def get_api_key():
    with open(API_KEY_PATH, 'r') as f:
        return f.read().strip()

def generate_challenges():
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    
    prompt = """
    I am a guitar player looking for creative chord voicing and extension challenges.
    Please generate a list of 50 distinct challenges.
    
    Examples of the types of challenges I want:
    * Play all the chords without the fifth
    * Add 9ths to every other chord
    * Play all the chords as triads using on the 2nd, 3rd, and 5th strings
    * Voice the chords such that there's always a note on the sixth string, and that note walks up the fretboard making minimal steps, jumping back to the bottom of the neck when you get to the 12th fret.
    * About once per verse, add an interesting passing chord with at least one non-diatonic note.
    
    Challenges should cover:
    1. Voicing challenges (specific intervals, string sets, inversions)
    2. Extension challenges (adding 7ths, 9ths, 11ths, 13ths)
    3. Insertion/Substitution challenges (passing chords, tritone subs, secondary dominants)

    Output strictly the list of 50 challenges, one per line, with no numbering or introductory text.
    """

    print(f"Requesting challenges from Gemini...")
    
    # Try the requested model first
    models_to_try = [MODEL_TAG_REQUESTED] + FALLBACK_MODELS
    
    response = None
    used_model = None

    for model_name in models_to_try:
        try:
            print(f"Attempting to generate with model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            used_model = model_name
            print("Success!")
            break
        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            continue
            
    if not response:
        print("All model attempts failed.")
        return

    try:
        text = response.text.strip()
        
        # Clean up if the model adds numbering
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_lines = []
        for line in lines:
            # Remove leading numbers like "1. " or "1) "
            if line[0].isdigit():
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    cleaned_lines.append(parts[1])
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
                
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
            
        print(f"Successfully generated {len(cleaned_lines)} challenges using {used_model} and saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error processing response: {e}")

if __name__ == "__main__":
    generate_challenges()
