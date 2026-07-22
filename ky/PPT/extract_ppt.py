import os
import sys
import glob

# Add explicit encoding
sys.stdout.reconfigure(encoding='utf-8')

ppt_dir = r"E:\note\考研\PPT"

try:
    import win32com.client
except ImportError:
    print("pywin32 not available")
    sys.exit(1)

output_dir = os.path.join(ppt_dir, "txt")
os.makedirs(output_dir, exist_ok=True)

powerpoint = win32com.client.Dispatch("PowerPoint.Application")

for fname in sorted(os.listdir(ppt_dir)):
    if not fname.endswith('.ppt'):
        continue

    fpath = os.path.join(ppt_dir, fname)
    # Use short path to avoid encoding issues
    print(f"Processing: {fname}")

    try:
        # Open with MsoTriState for WithWindow
        presentation = powerpoint.Presentations.Open(fpath, WithWindow=0)
        lines = []
        for i, slide in enumerate(presentation.Slides):
            lines.append(f"\n--- Slide {i+1} ---")
            for shape in slide.Shapes:
                if shape.HasTextFrame:
                    # Handle both TextFrame and TextFrame2
                    try:
                        text = shape.TextFrame.TextRange.Text.strip()
                        if text:
                            lines.append(text)
                    except:
                        pass
        presentation.Close()

        # Output file: use base name without extension
        base = os.path.splitext(fname)[0]
        outpath = os.path.join(output_dir, base + ".txt")
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"  -> {len(lines)} lines saved")
    except Exception as e:
        print(f"  Error: {e}")

powerpoint.Quit()
print("Done!")
