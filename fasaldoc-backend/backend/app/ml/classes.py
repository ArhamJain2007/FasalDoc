"""
PlantVillage 38-class label map with display-friendly names
and multilingual support (English, Hindi, Punjabi).
"""

PLANT_DISEASE_CLASSES: list[str] = [
    "Apple___Apple_scab",             # 0
    "Apple___Black_rot",              # 1
    "Apple___Cedar_apple_rust",       # 2
    "Apple___healthy",                # 3
    "Blueberry___healthy",            # 4
    "Cherry___Powdery_mildew",        # 5
    "Cherry___healthy",               # 6
    "Corn___Cercospora_leaf_spot",    # 7
    "Corn___Common_rust",             # 8
    "Corn___Northern_Leaf_Blight",    # 9
    "Corn___healthy",                 # 10
    "Grape___Black_rot",              # 11
    "Grape___Esca_Black_Measles",     # 12
    "Grape___Leaf_blight",            # 13
    "Grape___healthy",                # 14
    "Orange___Haunglongbing",         # 15
    "Peach___Bacterial_spot",         # 16
    "Peach___healthy",                # 17
    "Pepper___Bacterial_spot",        # 18
    "Pepper___healthy",               # 19
    "Potato___Early_blight",          # 20
    "Potato___Late_blight",           # 21
    "Potato___healthy",               # 22
    "Raspberry___healthy",            # 23
    "Rice___Brown_spot",              # 24  Added: major Indian crop
    "Rice___Leaf_blast",              # 25  Added: major Indian crop
    "Rice___Neck_blast",              # 26  Added: major Indian crop
    "Soybean___healthy",              # 27
    "Squash___Powdery_mildew",        # 28
    "Strawberry___Leaf_scorch",       # 29
    "Strawberry___healthy",           # 30
    "Tomato___Bacterial_spot",        # 31
    "Tomato___Early_blight",          # 32
    "Tomato___Late_blight",           # 33
    "Tomato___Leaf_Mold",             # 34
    "Tomato___Septoria_leaf_spot",    # 35
    "Tomato___Spider_mites",          # 36
    "Wheat___Brown_rust",             # 37  Added: major Indian crop
]

# Map class label to DB disease ID
CLASS_TO_DISEASE_ID: dict[str, str] = {
    "Apple___Apple_scab": "apple_apple_scab",
    "Apple___Black_rot": "apple_black_rot",
    "Apple___Cedar_apple_rust": "apple_cedar_rust",
    "Apple___healthy": "apple_healthy",
    "Blueberry___healthy": "blueberry_healthy",
    "Cherry___Powdery_mildew": "cherry_powdery_mildew",
    "Cherry___healthy": "cherry_healthy",
    "Corn___Cercospora_leaf_spot": "corn_cercospora",
    "Corn___Common_rust": "corn_common_rust",
    "Corn___Northern_Leaf_Blight": "corn_northern_leaf_blight",
    "Corn___healthy": "corn_healthy",
    "Grape___Black_rot": "grape_black_rot",
    "Grape___Esca_Black_Measles": "grape_esca",
    "Grape___Leaf_blight": "grape_leaf_blight",
    "Grape___healthy": "grape_healthy",
    "Orange___Haunglongbing": "orange_hlb",
    "Peach___Bacterial_spot": "peach_bacterial_spot",
    "Peach___healthy": "peach_healthy",
    "Pepper___Bacterial_spot": "pepper_bacterial_spot",
    "Pepper___healthy": "pepper_healthy",
    "Potato___Early_blight": "potato_early_blight",
    "Potato___Late_blight": "potato_late_blight",
    "Potato___healthy": "potato_healthy",
    "Raspberry___healthy": "raspberry_healthy",
    "Rice___Brown_spot": "rice_brown_spot",
    "Rice___Leaf_blast": "rice_leaf_blast",
    "Rice___Neck_blast": "rice_neck_blast",
    "Soybean___healthy": "soybean_healthy",
    "Squash___Powdery_mildew": "squash_powdery_mildew",
    "Strawberry___Leaf_scorch": "strawberry_leaf_scorch",
    "Strawberry___healthy": "strawberry_healthy",
    "Tomato___Bacterial_spot": "tomato_bacterial_spot",
    "Tomato___Early_blight": "tomato_early_blight",
    "Tomato___Late_blight": "tomato_late_blight",
    "Tomato___Leaf_Mold": "tomato_leaf_mold",
    "Tomato___Septoria_leaf_spot": "tomato_septoria",
    "Tomato___Spider_mites": "tomato_spider_mites",
    "Wheat___Brown_rust": "wheat_brown_rust",
}

# Display-friendly names (for API response)
DISEASE_DISPLAY: dict[str, dict[str, str]] = {
    "Apple___Apple_scab": {
        "disease_name": "Apple Scab",
        "crop_name": "Apple",
        "disease_name_hi": "सेब खुरच",
        "disease_name_pa": "ਸੇਬ ਖੁਰਚ",
        "crop_name_hi": "सेब",
        "crop_name_pa": "ਸੇਬ",
    },
    "Apple___Black_rot": {
        "disease_name": "Black Rot",
        "crop_name": "Apple",
        "disease_name_hi": "काला सड़न",
        "disease_name_pa": "ਕਾਲਾ ਸੜਨ",
        "crop_name_hi": "सेब",
        "crop_name_pa": "ਸੇਬ",
    },
    "Apple___Cedar_apple_rust": {
        "disease_name": "Cedar Apple Rust",
        "crop_name": "Apple",
        "disease_name_hi": "देवदार सेब किट्ट",
        "disease_name_pa": "ਸੀਡਰ ਸੇਬ ਕਿੱਟ",
        "crop_name_hi": "सेब",
        "crop_name_pa": "ਸੇਬ",
    },
    "Apple___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Apple",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "सेब",
        "crop_name_pa": "ਸੇਬ",
    },
    "Blueberry___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Blueberry",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "ब्लूबेरी",
        "crop_name_pa": "ਬਲੂਬੇਰੀ",
    },
    "Cherry___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "crop_name": "Cherry",
        "disease_name_hi": "चूर्णिल आसिता",
        "disease_name_pa": "ਪਾਊਡਰੀ ਮਿਲਡਿਊ",
        "crop_name_hi": "चेरी",
        "crop_name_pa": "ਚੈਰੀ",
    },
    "Cherry___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Cherry",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "चेरी",
        "crop_name_pa": "ਚੈਰੀ",
    },
    "Corn___Cercospora_leaf_spot": {
        "disease_name": "Gray Leaf Spot",
        "crop_name": "Corn",
        "disease_name_hi": "सर्कोस्पोरा पत्ती धब्बा",
        "disease_name_pa": "ਸਰਕੋਸਪੋਰਾ ਪੱਤੀ ਧੱਬਾ",
        "crop_name_hi": "मक्का",
        "crop_name_pa": "ਮੱਕੀ",
    },
    "Corn___Common_rust": {
        "disease_name": "Common Rust",
        "crop_name": "Corn",
        "disease_name_hi": "सामान्य किट्ट",
        "disease_name_pa": "ਸਾਧਾਰਨ ਕਿੱਟ",
        "crop_name_hi": "मक्का",
        "crop_name_pa": "ਮੱਕੀ",
    },
    "Corn___Northern_Leaf_Blight": {
        "disease_name": "Northern Leaf Blight",
        "crop_name": "Corn",
        "disease_name_hi": "उत्तरी पत्ती झुलसा",
        "disease_name_pa": "ਉੱਤਰੀ ਪੱਤੀ ਝੁਲਸ",
        "crop_name_hi": "मक्का",
        "crop_name_pa": "ਮੱਕੀ",
    },
    "Corn___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Corn",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "मक्का",
        "crop_name_pa": "ਮੱਕੀ",
    },
    "Grape___Black_rot": {
        "disease_name": "Black Rot",
        "crop_name": "Grape",
        "disease_name_hi": "काला सड़न",
        "disease_name_pa": "ਕਾਲਾ ਸੜਨ",
        "crop_name_hi": "अंगूर",
        "crop_name_pa": "ਅੰਗੂਰ",
    },
    "Grape___Esca_Black_Measles": {
        "disease_name": "Esca (Black Measles)",
        "crop_name": "Grape",
        "disease_name_hi": "एस्का (काली खसरा)",
        "disease_name_pa": "ਏਸਕਾ (ਕਾਲੀ ਖਸਰਾ)",
        "crop_name_hi": "अंगूर",
        "crop_name_pa": "ਅੰਗੂਰ",
    },
    "Grape___Leaf_blight": {
        "disease_name": "Leaf Blight",
        "crop_name": "Grape",
        "disease_name_hi": "पत्ती झुलसा",
        "disease_name_pa": "ਪੱਤੀ ਝੁਲਸ",
        "crop_name_hi": "अंगूर",
        "crop_name_pa": "ਅੰਗੂਰ",
    },
    "Grape___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Grape",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "अंगूर",
        "crop_name_pa": "ਅੰਗੂਰ",
    },
    "Orange___Haunglongbing": {
        "disease_name": "Huanglongbing (Citrus Greening)",
        "crop_name": "Orange",
        "disease_name_hi": "हुआंगलोंगबिंग",
        "disease_name_pa": "ਹੁਆਂਗਲੋਂਗਬਿੰਗ",
        "crop_name_hi": "संतरा",
        "crop_name_pa": "ਸੰਤਰਾ",
    },
    "Peach___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "crop_name": "Peach",
        "disease_name_hi": "जीवाणु धब्बा",
        "disease_name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ",
        "crop_name_hi": "आड़ू",
        "crop_name_pa": "ਆੜੂ",
    },
    "Peach___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Peach",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "आड़ू",
        "crop_name_pa": "ਆੜੂ",
    },
    "Pepper___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "crop_name": "Pepper",
        "disease_name_hi": "जीवाणु धब्बा",
        "disease_name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ",
        "crop_name_hi": "मिर्च",
        "crop_name_pa": "ਮਿਰਚ",
    },
    "Pepper___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Pepper",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "मिर्च",
        "crop_name_pa": "ਮਿਰਚ",
    },
    "Potato___Early_blight": {
        "disease_name": "Early Blight",
        "crop_name": "Potato",
        "disease_name_hi": "अगेती झुलसा",
        "disease_name_pa": "ਅਗੇਤੀ ਝੁਲਸ",
        "crop_name_hi": "आलू",
        "crop_name_pa": "ਆਲੂ",
    },
    "Potato___Late_blight": {
        "disease_name": "Late Blight",
        "crop_name": "Potato",
        "disease_name_hi": "पछेती झुलसा",
        "disease_name_pa": "ਪਛੇਤੀ ਝੁਲਸ",
        "crop_name_hi": "आलू",
        "crop_name_pa": "ਆਲੂ",
    },
    "Potato___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Potato",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "आलू",
        "crop_name_pa": "ਆਲੂ",
    },
    "Raspberry___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Raspberry",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "रसभरी",
        "crop_name_pa": "ਰਸਭਰੀ",
    },
    "Rice___Brown_spot": {
        "disease_name": "Brown Spot",
        "crop_name": "Rice",
        "disease_name_hi": "भूरा धब्बा",
        "disease_name_pa": "ਭੂਰਾ ਧੱਬਾ",
        "crop_name_hi": "चावल",
        "crop_name_pa": "ਚਾਵਲ",
    },
    "Rice___Leaf_blast": {
        "disease_name": "Leaf Blast",
        "crop_name": "Rice",
        "disease_name_hi": "पत्ती झुलसा",
        "disease_name_pa": "ਪੱਤੀ ਝੁਲਸ",
        "crop_name_hi": "चावल",
        "crop_name_pa": "ਚਾਵਲ",
    },
    "Rice___Neck_blast": {
        "disease_name": "Neck Blast",
        "crop_name": "Rice",
        "disease_name_hi": "गर्दन झुलसा",
        "disease_name_pa": "ਗਰਦਨ ਝੁਲਸ",
        "crop_name_hi": "चावल",
        "crop_name_pa": "ਚਾਵਲ",
    },
    "Soybean___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Soybean",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "सोयाबीन",
        "crop_name_pa": "ਸੋਇਆਬੀਨ",
    },
    "Squash___Powdery_mildew": {
        "disease_name": "Powdery Mildew",
        "crop_name": "Squash",
        "disease_name_hi": "चूर्णिल आसिता",
        "disease_name_pa": "ਪਾਊਡਰੀ ਮਿਲਡਿਊ",
        "crop_name_hi": "कद्दू",
        "crop_name_pa": "ਕੱਦੂ",
    },
    "Strawberry___Leaf_scorch": {
        "disease_name": "Leaf Scorch",
        "crop_name": "Strawberry",
        "disease_name_hi": "पत्ती झुलसन",
        "disease_name_pa": "ਪੱਤੀ ਝੁਲਸਣ",
        "crop_name_hi": "स्ट्रॉबेरी",
        "crop_name_pa": "ਸਟ੍ਰਾਬੇਰੀ",
    },
    "Strawberry___healthy": {
        "disease_name": "Healthy",
        "crop_name": "Strawberry",
        "disease_name_hi": "स्वस्थ",
        "disease_name_pa": "ਸਿਹਤਮੰਦ",
        "crop_name_hi": "स्ट्रॉबेरी",
        "crop_name_pa": "ਸਟ੍ਰਾਬੇਰੀ",
    },
    "Tomato___Bacterial_spot": {
        "disease_name": "Bacterial Spot",
        "crop_name": "Tomato",
        "disease_name_hi": "जीवाणु धब्बा",
        "disease_name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Tomato___Early_blight": {
        "disease_name": "Early Blight",
        "crop_name": "Tomato",
        "disease_name_hi": "अगेती झुलसा",
        "disease_name_pa": "ਅਗੇਤੀ ਝੁਲਸ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Tomato___Late_blight": {
        "disease_name": "Late Blight",
        "crop_name": "Tomato",
        "disease_name_hi": "पछेती झुलसा",
        "disease_name_pa": "ਪਛੇਤੀ ਝੁਲਸ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Tomato___Leaf_Mold": {
        "disease_name": "Leaf Mold",
        "crop_name": "Tomato",
        "disease_name_hi": "पत्ती फफूंदी",
        "disease_name_pa": "ਪੱਤੀ ਉੱਲੀ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Tomato___Septoria_leaf_spot": {
        "disease_name": "Septoria Leaf Spot",
        "crop_name": "Tomato",
        "disease_name_hi": "सेप्टोरिया पत्ती धब्बा",
        "disease_name_pa": "ਸੈਪਟੋਰੀਆ ਪੱਤੀ ਧੱਬਾ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Tomato___Spider_mites": {
        "disease_name": "Spider Mites (Two-spotted)",
        "crop_name": "Tomato",
        "disease_name_hi": "मकड़ी घुन",
        "disease_name_pa": "ਮੱਕੜੀ ਘੁਣ",
        "crop_name_hi": "टमाटर",
        "crop_name_pa": "ਟਮਾਟਰ",
    },
    "Wheat___Brown_rust": {
        "disease_name": "Brown Rust",
        "crop_name": "Wheat",
        "disease_name_hi": "भूरा किट्ट",
        "disease_name_pa": "ਭੂਰਾ ਕਿੱਟ",
        "crop_name_hi": "गेहूं",
        "crop_name_pa": "ਕਣਕ",
    },
}
