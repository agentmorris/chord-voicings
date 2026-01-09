from bs4 import BeautifulSoup
import gemini_client
import chord_generator
import re

def clean_chord(text):
    # Remove non-breaking spaces and extra whitespace
    text = text.replace('\xa0', ' ').strip()
    return text

def process_song(html_content, challenge):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all chord rows
    # Select tr with class 'ch'
    chord_rows = soup.find_all('tr', class_='ch')
    
    # Collect all chords and their locations
    # Location: (row_obj, chord_text)
    # We want to process chords in order.
    
    all_chords = []
    row_chords_map = {} # Map row_id (or index) to list of indices in all_chords
    
    for i, row in enumerate(chord_rows):
        cells = row.find_all('td')
        row_indices = []
        for cell in cells:
            text = clean_chord(cell.get_text())
            if text:
                # It's a chord (or at least text in a chord row)
                # Some might be empty/arrows/etc.
                # Heuristic: Chords usually start with A-G.
                if re.match(r'^[A-G]', text):
                    all_chords.append(text)
                    row_indices.append(len(all_chords) - 1)
        
        if row_indices:
            row_chords_map[i] = row_indices
            
    if not all_chords:
        return str(soup)
        
    # Get voicings from Gemini
    # We pass the list of chords.
    print(f"getting voicings for {len(all_chords)} chords")
    voicings = gemini_client.get_voicings(challenge, all_chords)
    
    if not voicings:
        print("No voicings returned")
        return str(soup)
        
    # Generate images and inject
    # We iterate through the rows we found.
    for i, row in enumerate(chord_rows):
        if i in row_chords_map:
            indices = row_chords_map[i]
            
            # Create a new cell for this row
            new_cell = soup.new_tag('td')
            new_cell['class'] = 'voicings'
            new_cell['style'] = 'vertical-align: top; padding-left: 20px;'
            
            # Container for images in this row
            container_div = soup.new_tag('div')
            container_div['style'] = 'display: flex; gap: 10px;'
            
            for chord_idx in indices:
                if chord_idx < len(voicings):
                    v_data = voicings[chord_idx]
                    
                    fingering = v_data.get('fingering', 'SKIP')
                    if fingering == 'SKIP':
                        continue
                        
                    chord_name = v_data.get('chord', all_chords[chord_idx])
                    start_fret = v_data.get('starting_fret', 1)
                    
                    # Generate image
                    img_base64 = chord_generator.generate_chord_image(fingering, chord_name, start_fret)
                    
                    if img_base64:
                        img_tag = soup.new_tag('img')
                        img_tag['src'] = f"data:image/png;base64,{img_base64}"
                        img_tag['alt'] = f"{chord_name} voicing"
                        img_tag['style'] = 'height: 100px; width: auto;' # Scale down a bit
                        container_div.append(img_tag)
            
            if container_div.contents:
                new_cell.append(container_div)
                row.append(new_cell)
                
    return str(soup)

if __name__ == "__main__":
    # Test with a snippet
    html = """
    <table>
    <tr class=ch><td>G&nbsp;</td><td>C/G&nbsp;</td></tr>
    <tr class=ly><td>Friday&nbsp;night</td><td></td></tr>
    </table>
    """
    processed = process_song(html, "Play all chords as triads")
    print(processed)
