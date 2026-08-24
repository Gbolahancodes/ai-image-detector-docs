from PIL.ExifTags import TAGS

def extract_metadata(image):
    metadata_dict = {}
    flags = []
    
    exif_data = image.getexif()
    if exif_data:
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            metadata_dict[tag_name] = str(value)[:100]
            
    for key, value in image.info.items():
        if key not in ['exif', 'icc_profile']:
            metadata_dict[key] = str(value)[:100]
            
    red_flags = ["photoshop", "adobe", "canva", "picsart", "gemini", "openai"]
    for key, val in metadata_dict.items():
        for keyword in red_flags:
            if keyword in str(val).lower():
                flags.append(f"Tool signature found: {val}")
                
    if len(flags) > 0: score = 100.0
    elif len(metadata_dict) < 6: score = 65.0
    else: score = 10.0
        
    return metadata_dict, flags, score