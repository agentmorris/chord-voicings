import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64

def generate_chord_image(fingering, chord_name, starting_fret=1):
    """
    Generates a guitar chord diagram.
    
    Args:
        fingering (str): String of 6 tokens separated by spaces, e.g. "x 3 2 0 1 0"
                         Tokens can be digits or 'x'/'X'.
        chord_name (str): Name of the chord to display.
        starting_fret (int): The fret number of the top-most line displayed.
        
    Returns:
        str: Base64 encoded PNG image.
    """
    
    # Parse fingering
    tokens = fingering.strip().split()
    if len(tokens) != 6:
        # Fallback for bad input
        print(f"Invalid fingering: {fingering}")
        return None

    parsed_frets = []
    for t in tokens:
        if t.lower() == 'x':
            parsed_frets.append(-1) # Muted
        elif t.isdigit():
            parsed_frets.append(int(t))
        else:
            parsed_frets.append(-1) # Treat unknown as muted
            
    # Determine fret range
    active_frets = [f for f in parsed_frets if f > 0]
    if not active_frets:
        min_fret = 1
        max_fret = 4 # Empty grid
    else:
        min_active = min(active_frets)
        max_active = max(active_frets)
        
        # If the chord fits within the first few frets, keep starting_fret at 1 unless specified
        if max_active <= 5 and starting_fret == 1:
            min_fret = 1
            max_fret = 5
        else:
            # If starting_fret is provided and > 1, use it
            if starting_fret > 1:
                min_fret = starting_fret
            else:
                # Heuristic: start near the lowest fingered note
                min_fret = max(1, min_active)
            
            # Ensure we show enough frets (at least 4 or 5)
            max_fret = max(min_fret + 4, max_active + 1)

    num_frets_to_draw = max_fret - min_fret + 1
    
    # Setup plot
    fig, ax = plt.subplots(figsize=(2.5, 3))
    
    # Remove axes
    ax.axis('off')
    
    # Drawing constants
    # Grid coordinates: x=0..5 (strings), y=0..num_frets (frets)
    # y=0 is the top (closest to nut)
    
    # Draw vertical lines (strings)
    for i in range(6):
        ax.plot([i, i], [0, num_frets_to_draw], color='black', linewidth=1)
        
    # Draw horizontal lines (frets)
    for i in range(num_frets_to_draw + 1):
        linewidth = 1
        if i == 0 and min_fret == 1:
            linewidth = 3 # Nut
        ax.plot([0, 5], [i, i], color='black', linewidth=linewidth)
        
    # Draw dots and indicators
    for string_idx, fret_val in enumerate(parsed_frets):
        x = string_idx
        
        if fret_val == -1:
            # Draw 'X' above nut
            ax.text(x, -0.4, 'x', ha='center', va='center', fontsize=12, fontweight='bold')
        elif fret_val == 0:
            # Draw 'O' above nut
            ax.text(x, -0.4, 'o', ha='center', va='center', fontsize=12, fontweight='bold')
        else:
            # Draw dot
            # Calculate y position relative to the grid we're drawing
            # Fret F is between line (F-min_fret) and (F-min_fret+1)
            # Actually, if min_fret=1:
            # Fret 1 is between y=0 and y=1.
            # We want to plot at y = (fret_val - min_fret) + 0.5
            
            relative_fret = fret_val - min_fret
            
            # Check if dot is within visible range
            if 0 <= relative_fret < num_frets_to_draw:
                circle = patches.Circle((x, relative_fret + 0.5), 0.35, color='black', zorder=2)
                ax.add_patch(circle)
    
    # Invert Y axis so nut is at top
    ax.invert_yaxis()
    
    # Add label for starting fret if > 1
    if min_fret > 1:
        ax.text(5.5, 0.5, f'{min_fret}fr', ha='left', va='center', fontsize=10)
        
    # Add chord name title
    ax.set_title(chord_name, pad=15, fontsize=14, fontweight='bold')
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    
    # Encode
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64

# Test
if __name__ == "__main__":
    # Test C Major
    print("Testing C Major...")
    img = generate_chord_image("x 3 2 0 1 0", "C")
    print(f"Generated base64 (first 50 chars): {img[:50]}...")
    
    # Test Bar Chord (G at 3rd fret)
    print("Testing G Bar...")
    img = generate_chord_image("3 5 5 4 3 3", "G", starting_fret=3)
    print(f"Generated base64 (first 50 chars): {img[:50]}...")

