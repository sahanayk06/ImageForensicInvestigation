import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import matplotlib.pyplot as plt
import os

def detect_fake_image(image_path):
    try:
        original = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Step 1: Recompress the image at 90% quality
    temp_path = "temp_ela.jpg"
    original.save(temp_path, 'JPEG', quality=90)
    compressed = Image.open(temp_path)

    # Step 2: Calculate ELA (difference between original and recompressed)
    ela_image = ImageChops.difference(original, compressed)
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    # Step 3: Convert ELA image to grayscale for analysis
    ela_gray = np.array(ela_image.convert('L'))
    mean_intensity = np.mean(ela_gray)
    std_intensity = np.std(ela_gray)

    # Step 4: Estimate forgery confidence (simple heuristic)
    confidence = min(100, (std_intensity / 25) * 100)
    confidence = round(confidence, 2)

    # Step 5: Show and save results
    output_path = os.path.join("images", "ELA_result.jpg")
    ela_image.save(output_path)

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(original)
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("ELA Result")
    plt.imshow(ela_image)
    plt.axis("off")

    plt.suptitle(f"Forgery Confidence: {confidence}%", fontsize=14, fontweight='bold')
    plt.show()

    print(f"\n✅ ELA result saved as: {output_path}")
    print(f"🔍 Estimated Forgery Confidence: {confidence}%")
