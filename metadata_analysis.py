from PIL import Image
from PIL.ExifTags import TAGS

def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()

        if not exifdata:
            print("No EXIF metadata found — might be edited or stripped.")
            return

        print("\nMetadata found:")
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            print(f"{tag:25}: {data}")
    except Exception as e:
        print(f"Error reading metadata: {e}")
