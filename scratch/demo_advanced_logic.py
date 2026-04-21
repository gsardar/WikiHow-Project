import re
import csv

def advanced_gender_detector(bio):
    # Normalize bio
    bio = bio.lower()
    
    # Precise Identity Markers (Avoiding metaphors like 'king' or 'queen')
    male_markers = [r'\bi am male\b', r'\bi am a (man|guy|boy)\b', r'\bhe/him\b', r'\bhis\b']
    female_markers = [r'\bi am female\b', r'\bi am a (woman|girl|gal)\b', r'\bshe/her\b', r'\bhers\b']
    nb_markers = [r'\bnon-binary\b', r'\bnonbinary\b', r'\bthey/them\b', r'\bgenderfluid\b', r'\bnb\b']
    
    is_male = any(re.search(p, bio) for p in male_markers)
    is_female = any(re.search(p, bio) for p in female_markers)
    is_nb = any(re.search(p, bio) for p in nb_markers)
    
    # Logic-Aware Resolution
    if is_nb:
        return "Non-Binary"
    if is_male and is_female:
        return "Non-Binary/Fluid"
    if is_male:
        return "Male"
    if is_female:
        return "Female"
    
    return "Unknown"

# Demo execution
profiles = [
    {"id": "User_Alpha", "bio": "I'm a female editor from New York. My pronouns are she/her."},
    {"id": "User_Beta", "bio": "Proudly representing the PNW. Most people use he/him when talking to me. I'm a guy into tech."},
    {"id": "User_Gamma", "bio": "I love editing WikiHow articles about science and space!"}
]

results = []
for p in profiles:
    gender = advanced_gender_detector(p['bio'])
    results.append({
        "User_ID": p['id'],
        "Detected_Gender": gender,
        "Bio_Snippet": p['bio'][:30] + "..."
    })

# Write results to demo CSV
output_file = r'f:\Users\Admin\Documents\WikiHow Project\scratch\demo_profile_extraction.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["User_ID", "Detected_Gender", "Bio_Snippet"])
    writer.writeheader()
    writer.writerows(results)

print(f"Demo extraction complete. Results saved to {output_file}")
