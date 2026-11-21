import os
from metadata_analysis import extract_metadata
from image_authentication import detect_fake_image
from generate_report import generate_dark_report


def main():
    print("\n🕵️ IMAGE FORENSIC INVESTIGATION TOOL 🧩")
    print("-------------------------------------------")

    image_folder = "images"

    if not os.path.exists(image_folder):
        print(f"❌ Folder '{image_folder}' not found. Please create it and add some images.")
        return

    images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not images:
        print(f"⚠️ No images found in '{image_folder}' folder.")
        return

    for img in images:
        image_path = os.path.join(image_folder, img)
        print(f"\n🔍 Analyzing: {img}")
        print("-" * 40)

        # 1️⃣ Extract metadata
        try:
            extract_metadata(image_path)
        except Exception as e:
            print("❌ Metadata extraction failed:", e)

        # 2️⃣ Run ELA forgery detection
        try:
            detect_fake_image(image_path)
        except Exception as e:
            print("❌ Forgery analysis failed:", e)

    print("\n✅ All analyses completed!")

if __name__ == "__main__":
    main()
