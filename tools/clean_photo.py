import os
import cv2
import numpy as np
from PIL import Image
import rembg
import argparse

def process_photo(input_path, output_path):
    print(f"Processing {input_path}...")
    
    # 1. Remove background
    with open(input_path, 'rb') as f:
        input_data = f.read()
    
    subject_data = rembg.remove(input_data)
    
    # Convert rembg output to OpenCV format (BGRA)
    nparr = np.frombuffer(subject_data, np.uint8)
    img_bgra = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    
    if img_bgra is None:
        raise ValueError("Could not decode image after background removal")
        
    # 2. Extract alpha channel and color channels
    b, g, r, a = cv2.split(img_bgra)
    img_bgr = cv2.merge([b, g, r])
    
    # Apply CLAHE to lightness channel in LAB color space
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a_chan, b_chan = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    limg = cv2.merge((cl, a_chan, b_chan))
    img_clahe = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # 3. Composite onto white background
    # Create white canvas
    canvas = np.ones_like(img_clahe) * 255
    
    # Create 3-channel alpha mask
    alpha_mask = a / 255.0
    alpha_mask_3c = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
    
    # Blend
    foreground = cv2.multiply(alpha_mask_3c, img_clahe.astype(float))
    background = cv2.multiply(1.0 - alpha_mask_3c, canvas.astype(float))
    out_img = cv2.add(foreground, background).astype(np.uint8)
    
    # Ensure assets directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save
    cv2.imwrite(output_path, out_img)
    print(f"Saved processed photo to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean photo for ASCII art")
    parser.add_argument("input", help="Path to input photo", nargs="?", default="my-photo.jpg")
    parser.add_argument("output", help="Path to output photo", nargs="?", default="assets/photo-ready.png")
    args = parser.parse_args()
    
    process_photo(args.input, args.output)
