"""
Seed diseases and treatments on first run.
Called during startup if the diseases table is empty.
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.disease import Disease
from app.models.treatment import Treatment

logger = structlog.get_logger()

DISEASE_SEED_DATA = [
    {
        "id": "tomato_early_blight",
        "class_index": 32,
        "name_en": "Early Blight",
        "name_hi": "अगेती झुलसा",
        "name_pa": "ਅਗੇਤੀ ਝੁਲਸ",
        "crop_en": "Tomato",
        "crop_hi": "टमाटर",
        "crop_pa": "ਟਮਾਟਰ",
        "description_en": "Early blight is a fungal disease caused by Alternaria solani. It causes dark spots with concentric rings on older leaves, leading to defoliation and reduced yield.",
        "description_hi": "अगेती झुलसा एक फफूंद रोग है जो Alternaria solani के कारण होता है। यह पुरानी पत्तियों पर केंद्रित छल्लों वाले काले धब्बे बनाता है।",
        "description_pa": "ਅਗੇਤੀ ਝੁਲਸ ਇੱਕ ਫੰਗਲ ਬਿਮਾਰੀ ਹੈ ਜੋ Alternaria solani ਕਾਰਨ ਹੁੰਦੀ ਹੈ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Mancozeb 75% WP",
                "name_hi": "मैन्कोज़ेब 75% WP",
                "name_pa": "ਮੈਨਕੋਜ਼ੇਬ 75% WP",
                "dosage": "2.5 g/L water",
                "schedule": "Spray every 7-10 days, 3-4 applications",
            },
            {
                "type": "organic",
                "name_en": "Neem oil spray",
                "name_hi": "नीम तेल स्प्रे",
                "name_pa": "ਨਿੰਮ ਤੇਲ ਸਪਰੇਅ",
                "dosage": "5 mL/L water",
                "schedule": "Spray every 7 days",
            },
        ],
    },
    {
        "id": "tomato_late_blight",
        "class_index": 33,
        "name_en": "Late Blight",
        "name_hi": "पछेती झुलसा",
        "name_pa": "ਪਛੇਤੀ ਝੁਲਸ",
        "crop_en": "Tomato",
        "crop_hi": "टमाटर",
        "crop_pa": "ਟਮਾਟਰ",
        "description_en": "Late blight is caused by Phytophthora infestans. It produces water-soaked lesions that rapidly turn dark brown, destroying entire plants within days under humid conditions.",
        "description_hi": "पछेती झुलसा Phytophthora infestans के कारण होता है। यह पानी से भीगे घाव उत्पन्न करता है जो तेजी से गहरे भूरे रंग के हो जाते हैं।",
        "description_pa": "ਪਛੇਤੀ ਝੁਲਸ Phytophthora infestans ਕਾਰਨ ਹੁੰਦੀ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Metalaxyl + Mancozeb",
                "name_hi": "मेटालैक्सिल + मैन्कोज़ेब",
                "name_pa": "ਮੇਟਾਲੈਕਸਿਲ + ਮੈਨਕੋਜ਼ੇਬ",
                "dosage": "2.5 g/L water",
                "schedule": "Spray every 7 days, start at first sign",
            },
            {
                "type": "organic",
                "name_en": "Bordeaux mixture (1%)",
                "name_hi": "बोर्डो मिश्रण (1%)",
                "name_pa": "ਬੋਰਡੋ ਮਿਸ਼ਰਣ (1%)",
                "dosage": "10 g copper sulphate + 10 g lime per L",
                "schedule": "Spray every 10 days preventively",
            },
        ],
    },
    {
        "id": "potato_early_blight",
        "class_index": 20,
        "name_en": "Early Blight",
        "name_hi": "अगेती झुलसा",
        "name_pa": "ਅਗੇਤੀ ਝੁਲਸ",
        "crop_en": "Potato",
        "crop_hi": "आलू",
        "crop_pa": "ਆਲੂ",
        "description_en": "Potato early blight caused by Alternaria solani appears as dark brown lesions with yellow halos on leaves, reducing photosynthesis and tuber yield.",
        "description_hi": "आलू की अगेती झुलसा Alternaria solani के कारण होती है और पत्तियों पर पीले हेलो के साथ गहरे भूरे घाव दिखाई देते हैं।",
        "description_pa": "ਆਲੂ ਦੀ ਅਗੇਤੀ ਝੁਲਸ Alternaria solani ਕਾਰਨ ਹੁੰਦੀ ਹੈ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Chlorothalonil 75% WP",
                "name_hi": "क्लोरोथैलोनिल 75% WP",
                "name_pa": "ਕਲੋਰੋਥੈਲੋਨਿਲ 75% WP",
                "dosage": "2 g/L water",
                "schedule": "Spray every 10-14 days",
            },
        ],
    },
    {
        "id": "potato_late_blight",
        "class_index": 21,
        "name_en": "Late Blight",
        "name_hi": "पछेती झुलसा",
        "name_pa": "ਪਛੇਤੀ ਝੁਲਸ",
        "crop_en": "Potato",
        "crop_hi": "आलू",
        "crop_pa": "ਆਲੂ",
        "description_en": "Potato late blight caused by Phytophthora infestans is one of the most destructive plant diseases, capable of wiping out entire fields within a week.",
        "description_hi": "आलू की पछेती झुलसा Phytophthora infestans के कारण होती है और सबसे विनाशकारी पौधों की बीमारियों में से एक है।",
        "description_pa": "ਆਲੂ ਦੀ ਪਛੇਤੀ ਝੁਲਸ Phytophthora infestans ਕਾਰਨ ਹੁੰਦੀ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Cymoxanil + Mancozeb",
                "name_hi": "साइमोक्सानिल + मैन्कोज़ेब",
                "name_pa": "ਸਾਈਮੋਕਸਾਨਿਲ + ਮੈਨਕੋਜ਼ੇਬ",
                "dosage": "3 g/L water",
                "schedule": "Spray at 7-day intervals, 3-4 sprays",
            },
        ],
    },
    {
        "id": "rice_brown_spot",
        "class_index": 24,
        "name_en": "Brown Spot",
        "name_hi": "भूरा धब्बा",
        "name_pa": "ਭੂਰਾ ਧੱਬਾ",
        "crop_en": "Rice",
        "crop_hi": "चावल",
        "crop_pa": "ਚਾਵਲ",
        "description_en": "Rice brown spot caused by Helminthosporium oryzae produces oval brown lesions on leaves and can cause significant yield loss, especially in nutrient-deficient soils.",
        "description_hi": "Helminthosporium oryzae के कारण चावल में भूरे धब्बे पड़ते हैं और पत्तियों पर अंडाकार भूरे घाव होते हैं।",
        "description_pa": "Helminthosporium oryzae ਕਾਰਨ ਚਾਵਲ ਵਿੱਚ ਭੂਰੇ ਧੱਬੇ ਪੈਂਦੇ ਹਨ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Propiconazole 25% EC",
                "name_hi": "प्रोपिकोनाज़ोल 25% EC",
                "name_pa": "ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC",
                "dosage": "1 mL/L water",
                "schedule": "2 sprays at 15-day interval",
            },
        ],
    },
    {
        "id": "rice_leaf_blast",
        "class_index": 25,
        "name_en": "Leaf Blast",
        "name_hi": "पत्ती झुलसा",
        "name_pa": "ਪੱਤੀ ਝੁਲਸ",
        "crop_en": "Rice",
        "crop_hi": "चावल",
        "crop_pa": "ਚਾਵਲ",
        "description_en": "Rice leaf blast caused by Magnaporthe oryzae is the most important rice disease globally. Diamond-shaped gray-green lesions appear on leaves.",
        "description_hi": "Magnaporthe oryzae के कारण चावल में पत्ती झुलसा होती है जो विश्व स्तर पर सबसे महत्वपूर्ण चावल रोग है।",
        "description_pa": "Magnaporthe oryzae ਕਾਰਨ ਚਾਵਲ ਵਿੱਚ ਪੱਤੀ ਝੁਲਸ ਹੁੰਦੀ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Tricyclazole 75% WP",
                "name_hi": "ट्राइसाइक्लाज़ोल 75% WP",
                "name_pa": "ਟਰਾਈਸਾਈਕਲਾਜ਼ੋਲ 75% WP",
                "dosage": "0.6 g/L water",
                "schedule": "Spray at tillering and panicle initiation",
            },
            {
                "type": "organic",
                "name_en": "Silicon-based soil amendment",
                "name_hi": "सिलिकॉन आधारित मृदा संशोधन",
                "name_pa": "ਸਿਲੀਕਾਨ ਆਧਾਰਿਤ ਮਿੱਟੀ ਸੁਧਾਰ",
                "dosage": "250 kg/ha calcium silicate",
                "schedule": "Apply at land preparation",
            },
        ],
    },
    {
        "id": "rice_neck_blast",
        "class_index": 26,
        "name_en": "Neck Blast",
        "name_hi": "गर्दन झुलसा",
        "name_pa": "ਗਰਦਨ ਝੁਲਸ",
        "crop_en": "Rice",
        "crop_hi": "चावल",
        "crop_pa": "ਚਾਵਲ",
        "description_en": "Rice neck blast affects the panicle neck, causing it to break and resulting in white empty panicles — one of the most yield-damaging forms of rice blast.",
        "description_hi": "चावल की गर्दन झुलसा बाली की गर्दन को प्रभावित करती है जिससे वह टूट जाती है।",
        "description_pa": "ਚਾਵਲ ਦੀ ਗਰਦਨ ਝੁਲਸ ਬਾਲੀ ਦੀ ਗਰਦਨ ਨੂੰ ਪ੍ਰਭਾਵਿਤ ਕਰਦੀ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Isoprothiolane 40% EC",
                "name_hi": "आइसोप्रोथिओलेन 40% EC",
                "name_pa": "ਆਈਸੋਪ੍ਰੋਥਿਓਲੇਨ 40% EC",
                "dosage": "1.5 mL/L water",
                "schedule": "Apply at boot stage and heading",
            },
        ],
    },
    {
        "id": "wheat_brown_rust",
        "class_index": 37,
        "name_en": "Brown Rust",
        "name_hi": "भूरा किट्ट",
        "name_pa": "ਭੂਰਾ ਕਿੱਟ",
        "crop_en": "Wheat",
        "crop_hi": "गेहूं",
        "crop_pa": "ਕਣਕ",
        "description_en": "Wheat brown rust caused by Puccinia triticina produces small orange-brown pustules on leaves. High humidity accelerates spread and can cause 30-70% yield loss.",
        "description_hi": "Puccinia triticina के कारण गेहूं में भूरा किट्ट होता है जो पत्तियों पर छोटे नारंगी-भूरे pustules बनाता है।",
        "description_pa": "Puccinia triticina ਕਾਰਨ ਕਣਕ ਵਿੱਚ ਭੂਰਾ ਕਿੱਟ ਹੁੰਦਾ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Propiconazole 25% EC",
                "name_hi": "प्रोपिकोनाज़ोल 25% EC",
                "name_pa": "ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC",
                "dosage": "1 mL/L water",
                "schedule": "Spray at first sign, repeat after 15 days",
            },
            {
                "type": "organic",
                "name_en": "Sulfur dust",
                "name_hi": "सल्फर धूल",
                "name_pa": "ਸਲਫਰ ਧੂੜ",
                "dosage": "20-25 kg/ha",
                "schedule": "Apply when disease is first noticed",
            },
        ],
    },
    {
        "id": "apple_apple_scab",
        "class_index": 0,
        "name_en": "Apple Scab",
        "name_hi": "सेब खुरच",
        "name_pa": "ਸੇਬ ਖੁਰਚ",
        "crop_en": "Apple",
        "crop_hi": "सेब",
        "crop_pa": "ਸੇਬ",
        "description_en": "Apple scab caused by Venturia inaequalis creates olive-green to black scabs on leaves and fruit, reducing fruit quality and marketability.",
        "description_hi": "Venturia inaequalis के कारण सेब में खुरच होती है जो पत्तियों और फल पर जैतून-हरे से काले धब्बे बनाती है।",
        "description_pa": "Venturia inaequalis ਕਾਰਨ ਸੇਬ ਵਿੱਚ ਖੁਰਚ ਹੁੰਦੀ ਹੈ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Captan 50% WP",
                "name_hi": "कैप्टन 50% WP",
                "name_pa": "ਕੈਪਟਨ 50% WP",
                "dosage": "3 g/L water",
                "schedule": "Spray at green tip, pink bud, petal fall stages",
            },
        ],
    },
    {
        "id": "apple_black_rot",
        "class_index": 1,
        "name_en": "Black Rot",
        "name_hi": "काला सड़न",
        "name_pa": "ਕਾਲਾ ਸੜਨ",
        "crop_en": "Apple",
        "crop_hi": "सेब",
        "crop_pa": "ਸੇਬ",
        "description_en": "Apple black rot caused by Botryosphaeria obtusa affects leaves, bark, and fruit. Infected fruit develops a black rot that can spread to entire fruit.",
        "description_hi": "Botryosphaeria obtusa के कारण सेब में काला सड़न होता है जो पत्तियों, छाल और फल को प्रभावित करता है।",
        "description_pa": "Botryosphaeria obtusa ਕਾਰਨ ਸੇਬ ਵਿੱਚ ਕਾਲਾ ਸੜਨ ਹੁੰਦਾ ਹੈ।",
        "severity": "high",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Thiophanate-methyl 70% WP",
                "name_hi": "थायोफेनेट-मिथाइल 70% WP",
                "name_pa": "ਥਾਈਓਫੇਨੇਟ-ਮਿਥਾਈਲ 70% WP",
                "dosage": "1 g/L water",
                "schedule": "Spray every 14 days during growing season",
            },
        ],
    },
    {
        "id": "corn_common_rust",
        "class_index": 8,
        "name_en": "Common Rust",
        "name_hi": "सामान्य किट्ट",
        "name_pa": "ਸਾਧਾਰਨ ਕਿੱਟ",
        "crop_en": "Corn",
        "crop_hi": "मक्का",
        "crop_pa": "ਮੱਕੀ",
        "description_en": "Corn common rust caused by Puccinia sorghi produces small cinnamon-brown pustules on both leaf surfaces. Heavy infection reduces photosynthesis and grain fill.",
        "description_hi": "Puccinia sorghi के कारण मक्के में सामान्य किट्ट होती है।",
        "description_pa": "Puccinia sorghi ਕਾਰਨ ਮੱਕੀ ਵਿੱਚ ਸਾਧਾਰਨ ਕਿੱਟ ਹੁੰਦੀ ਹੈ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Mancozeb 75% WP",
                "name_hi": "मैन्कोज़ेब 75% WP",
                "name_pa": "ਮੈਨਕੋਜ਼ੇਬ 75% WP",
                "dosage": "2.5 g/L water",
                "schedule": "Spray at first sign, repeat at 10-day intervals",
            },
        ],
    },
    {
        "id": "tomato_bacterial_spot",
        "class_index": 31,
        "name_en": "Bacterial Spot",
        "name_hi": "जीवाणु धब्बा",
        "name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ",
        "crop_en": "Tomato",
        "crop_hi": "टमाटर",
        "crop_pa": "ਟਮਾਟਰ",
        "description_en": "Tomato bacterial spot caused by Xanthomonas vesicatoria causes water-soaked spots on leaves and fruit, leading to defoliation and blemished fruit.",
        "description_hi": "Xanthomonas vesicatoria के कारण टमाटर में जीवाणु धब्बा होता है।",
        "description_pa": "Xanthomonas vesicatoria ਕਾਰਨ ਟਮਾਟਰ ਵਿੱਚ ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ ਹੁੰਦਾ ਹੈ।",
        "severity": "medium",
        "treatments": [
            {
                "type": "chemical",
                "name_en": "Copper oxychloride 50% WP",
                "name_hi": "कॉपर ऑक्सीक्लोराइड 50% WP",
                "name_pa": "ਕਾਪਰ ਆਕਸੀਕਲੋਰਾਈਡ 50% WP",
                "dosage": "3 g/L water",
                "schedule": "Spray every 7-10 days, 3-4 applications",
            },
        ],
    },
]

# Healthy class stubs
HEALTHY_CLASSES = [
    {"id": "apple_healthy", "class_index": 3, "crop_en": "Apple", "crop_hi": "सेब", "crop_pa": "ਸੇਬ"},
    {"id": "blueberry_healthy", "class_index": 4, "crop_en": "Blueberry", "crop_hi": "ब्लूबेरी", "crop_pa": "ਬਲੂਬੇਰੀ"},
    {"id": "cherry_healthy", "class_index": 6, "crop_en": "Cherry", "crop_hi": "चेरी", "crop_pa": "ਚੈਰੀ"},
    {"id": "corn_healthy", "class_index": 10, "crop_en": "Corn", "crop_hi": "मक्का", "crop_pa": "ਮੱਕੀ"},
    {"id": "grape_healthy", "class_index": 14, "crop_en": "Grape", "crop_hi": "अंगूर", "crop_pa": "ਅੰਗੂਰ"},
    {"id": "peach_healthy", "class_index": 17, "crop_en": "Peach", "crop_hi": "आड़ू", "crop_pa": "ਆੜੂ"},
    {"id": "pepper_healthy", "class_index": 19, "crop_en": "Pepper", "crop_hi": "मिर्च", "crop_pa": "ਮਿਰਚ"},
    {"id": "potato_healthy", "class_index": 22, "crop_en": "Potato", "crop_hi": "आलू", "crop_pa": "ਆਲੂ"},
    {"id": "raspberry_healthy", "class_index": 23, "crop_en": "Raspberry", "crop_hi": "रसभरी", "crop_pa": "ਰਸਭਰੀ"},
    {"id": "soybean_healthy", "class_index": 27, "crop_en": "Soybean", "crop_hi": "सोयाबीन", "crop_pa": "ਸੋਇਆਬੀਨ"},
    {"id": "strawberry_healthy", "class_index": 30, "crop_en": "Strawberry", "crop_hi": "स्ट्रॉबेरी", "crop_pa": "ਸਟ੍ਰਾਬੇਰੀ"},
    {"id": "tomato_healthy", "class_index": 38, "crop_en": "Tomato", "crop_hi": "टमाटर", "crop_pa": "ਟਮਾਟਰ"},
]

REMAINING_DISEASES = [
    {"id": "apple_cedar_rust", "class_index": 2, "name_en": "Cedar Apple Rust", "name_hi": "देवदार सेब किट्ट", "name_pa": "ਸੀਡਰ ਸੇਬ ਕਿੱਟ", "crop_en": "Apple", "crop_hi": "सेब", "crop_pa": "ਸੇਬ", "description_en": "Cedar apple rust caused by Gymnosporangium juniperi-virginianae creates bright orange-yellow spots on apple leaves.", "description_hi": "देवदार सेब किट्ट सेब की पत्तियों पर चमकीले नारंगी-पीले धब्बे बनाता है।", "description_pa": "ਸੀਡਰ ਸੇਬ ਕਿੱਟ ਸੇਬ ਦੀਆਂ ਪੱਤੀਆਂ ਤੇ ਚਮਕਦਾਰ ਸੰਤਰੀ-ਪੀਲੇ ਧੱਬੇ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "medium"},
    {"id": "cherry_powdery_mildew", "class_index": 5, "name_en": "Powdery Mildew", "name_hi": "चूर्णिल आसिता", "name_pa": "ਪਾਊਡਰੀ ਮਿਲਡਿਊ", "crop_en": "Cherry", "crop_hi": "चेरी", "crop_pa": "ਚੈਰੀ", "description_en": "Cherry powdery mildew caused by Podosphaera clandestina creates white powdery coating on leaves and young shoots.", "description_hi": "Podosphaera clandestina के कारण चेरी में चूर्णिल आसिता पत्तियों पर सफेद पाउडर जैसी परत बनाती है।", "description_pa": "ਚੈਰੀ ਵਿੱਚ ਪਾਊਡਰੀ ਮਿਲਡਿਊ ਪੱਤੀਆਂ ਤੇ ਚਿੱਟੀ ਪਰਤ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "low"},
    {"id": "corn_cercospora", "class_index": 7, "name_en": "Cercospora Leaf Spot", "name_hi": "सर्कोस्पोरा पत्ती धब्बा", "name_pa": "ਸਰਕੋਸਪੋਰਾ ਪੱਤੀ ਧੱਬਾ", "crop_en": "Corn", "crop_hi": "मक्का", "crop_pa": "ਮੱਕੀ", "description_en": "Corn gray leaf spot caused by Cercospora zeae-maydis creates rectangular gray-brown lesions on leaves.", "description_hi": "मक्के में सर्कोस्पोरा पत्ती धब्बा आयताकार भूरे घाव बनाता है।", "description_pa": "ਮੱਕੀ ਵਿੱਚ ਸਰਕੋਸਪੋਰਾ ਆਇਤਾਕਾਰ ਭੂਰੇ ਘਾਅ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "medium"},
    {"id": "corn_northern_leaf_blight", "class_index": 9, "name_en": "Northern Leaf Blight", "name_hi": "उत्तरी पत्ती झुलसा", "name_pa": "ਉੱਤਰੀ ਪੱਤੀ ਝੁਲਸ", "crop_en": "Corn", "crop_hi": "मक्का", "crop_pa": "ਮੱਕੀ", "description_en": "Caused by Exserohilum turcicum, northern leaf blight produces long cigar-shaped gray-green lesions on corn leaves.", "description_hi": "मक्के में उत्तरी पत्ती झुलसा लंबे सिगार के आकार के घाव बनाता है।", "description_pa": "ਮੱਕੀ ਵਿੱਚ ਉੱਤਰੀ ਪੱਤੀ ਝੁਲਸ ਲੰਬੇ ਘਾਅ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "medium"},
    {"id": "grape_black_rot", "class_index": 11, "name_en": "Black Rot", "name_hi": "काला सड़न", "name_pa": "ਕਾਲਾ ਸੜਨ", "crop_en": "Grape", "crop_hi": "अंगूर", "crop_pa": "ਅੰਗੂਰ", "description_en": "Grape black rot caused by Guignardia bidwellii causes brown lesions on leaves and mummifies the fruit.", "description_hi": "Guignardia bidwellii के कारण अंगूर में काला सड़न पत्तियों पर भूरे घाव बनाता है।", "description_pa": "Guignardia bidwellii ਕਾਰਨ ਅੰਗੂਰ ਵਿੱਚ ਕਾਲਾ ਸੜਨ ਹੁੰਦਾ ਹੈ।", "severity": "high"},
    {"id": "grape_esca", "class_index": 12, "name_en": "Esca (Black Measles)", "name_hi": "एस्का (काली खसरा)", "name_pa": "ਏਸਕਾ (ਕਾਲੀ ਖਸਰਾ)", "crop_en": "Grape", "crop_hi": "अंगूर", "crop_pa": "ਅੰਗੂਰ", "description_en": "Esca is a complex grapevine trunk disease causing tiger-stripe patterns on leaves and internal wood decay.", "description_hi": "एस्का अंगूर के तने की एक जटिल बीमारी है जो पत्तियों पर टाइगर-स्ट्राइप पैटर्न बनाती है।", "description_pa": "ਏਸਕਾ ਅੰਗੂਰ ਦੀ ਇੱਕ ਗੁੰਝਲਦਾਰ ਬਿਮਾਰੀ ਹੈ।", "severity": "high"},
    {"id": "grape_leaf_blight", "class_index": 13, "name_en": "Leaf Blight", "name_hi": "पत्ती झुलसा", "name_pa": "ਪੱਤੀ ਝੁਲਸ", "crop_en": "Grape", "crop_hi": "अंगूर", "crop_pa": "ਅੰਗੂਰ", "description_en": "Grape leaf blight caused by Pseudocercospora vitis creates irregular dark spots on leaves.", "description_hi": "Pseudocercospora vitis के कारण अंगूर में पत्ती झुलसा अनियमित काले धब्बे बनाती है।", "description_pa": "ਅੰਗੂਰ ਵਿੱਚ ਪੱਤੀ ਝੁਲਸ ਅਨਿਯਮਿਤ ਕਾਲੇ ਧੱਬੇ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "medium"},
    {"id": "orange_hlb", "class_index": 15, "name_en": "Huanglongbing (Citrus Greening)", "name_hi": "हुआंगलोंगबिंग", "name_pa": "ਹੁਆਂਗਲੋਂਗਬਿੰਗ", "crop_en": "Orange", "crop_hi": "संतरा", "crop_pa": "ਸੰਤਰਾ", "description_en": "Huanglongbing is a devastating citrus disease caused by Candidatus Liberibacter bacteria, causing blotchy leaf mottle and misshapen fruit.", "description_hi": "हुआंगलोंगबिंग एक विनाशकारी खट्टे फल की बीमारी है।", "description_pa": "ਹੁਆਂਗਲੋਂਗਬਿੰਗ ਇੱਕ ਵਿਨਾਸ਼ਕਾਰੀ ਨਿੰਬੂ ਦੀ ਬਿਮਾਰੀ ਹੈ।", "severity": "high"},
    {"id": "peach_bacterial_spot", "class_index": 16, "name_en": "Bacterial Spot", "name_hi": "जीवाणु धब्बा", "name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ", "crop_en": "Peach", "crop_hi": "आड़ू", "crop_pa": "ਆੜੂ", "description_en": "Peach bacterial spot caused by Xanthomonas arboricola causes water-soaked lesions on leaves and pitting on fruit.", "description_hi": "Xanthomonas arboricola के कारण आड़ू में जीवाणु धब्बा होता है।", "description_pa": "Xanthomonas arboricola ਕਾਰਨ ਆੜੂ ਵਿੱਚ ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ ਹੁੰਦਾ ਹੈ।", "severity": "medium"},
    {"id": "pepper_bacterial_spot", "class_index": 18, "name_en": "Bacterial Spot", "name_hi": "जीवाणु धब्बा", "name_pa": "ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ", "crop_en": "Pepper", "crop_hi": "मिर्च", "crop_pa": "ਮਿਰਚ", "description_en": "Pepper bacterial spot caused by Xanthomonas euvesicatoria leads to dark water-soaked spots on leaves and fruit.", "description_hi": "Xanthomonas euvesicatoria के कारण मिर्च में जीवाणु धब्बा होता है।", "description_pa": "ਮਿਰਚ ਵਿੱਚ ਬੈਕਟੀਰੀਅਲ ਧੱਬਾ ਹੁੰਦਾ ਹੈ।", "severity": "medium"},
    {"id": "squash_powdery_mildew", "class_index": 28, "name_en": "Powdery Mildew", "name_hi": "चूर्णिल आसिता", "name_pa": "ਪਾਊਡਰੀ ਮਿਲਡਿਊ", "crop_en": "Squash", "crop_hi": "कद्दू", "crop_pa": "ਕੱਦੂ", "description_en": "Squash powdery mildew caused by Podosphaera xanthii creates white powdery patches on leaves, reducing photosynthesis.", "description_hi": "Podosphaera xanthii के कारण कद्दू में चूर्णिल आसिता होती है।", "description_pa": "ਕੱਦੂ ਵਿੱਚ ਪਾਊਡਰੀ ਮਿਲਡਿਊ ਹੁੰਦੀ ਹੈ।", "severity": "low"},
    {"id": "strawberry_leaf_scorch", "class_index": 29, "name_en": "Leaf Scorch", "name_hi": "पत्ती झुलसन", "name_pa": "ਪੱਤੀ ਝੁਲਸਣ", "crop_en": "Strawberry", "crop_hi": "स्ट्रॉबेरी", "crop_pa": "ਸਟ੍ਰਾਬੇਰੀ", "description_en": "Strawberry leaf scorch caused by Diplocarpon earlianum creates small dark purple spots on leaves that coalesce causing leaf death.", "description_hi": "Diplocarpon earlianum के कारण स्ट्रॉबेरी में पत्ती झुलसन होती है।", "description_pa": "ਸਟ੍ਰਾਬੇਰੀ ਵਿੱਚ ਪੱਤੀ ਝੁਲਸਣ ਹੁੰਦੀ ਹੈ।", "severity": "medium"},
    {"id": "tomato_leaf_mold", "class_index": 34, "name_en": "Leaf Mold", "name_hi": "पत्ती फफूंदी", "name_pa": "ਪੱਤੀ ਉੱਲੀ", "crop_en": "Tomato", "crop_hi": "टमाटर", "crop_pa": "ਟਮਾਟਰ", "description_en": "Tomato leaf mold caused by Passalora fulva creates pale green-yellow spots on upper leaf surfaces with olive-green mold on the underside.", "description_hi": "Passalora fulva के कारण टमाटर में पत्ती फफूंदी होती है।", "description_pa": "ਟਮਾਟਰ ਵਿੱਚ ਪੱਤੀ ਉੱਲੀ ਹੁੰਦੀ ਹੈ।", "severity": "medium"},
    {"id": "tomato_septoria", "class_index": 35, "name_en": "Septoria Leaf Spot", "name_hi": "सेप्टोरिया पत्ती धब्बा", "name_pa": "ਸੈਪਟੋਰੀਆ ਪੱਤੀ ਧੱਬਾ", "crop_en": "Tomato", "crop_hi": "टमाटर", "crop_pa": "ਟਮਾਟਰ", "description_en": "Septoria leaf spot caused by Septoria lycopersici creates small circular spots with white centers and dark borders on tomato leaves.", "description_hi": "Septoria lycopersici के कारण टमाटर में सेप्टोरिया पत्ती धब्बा होता है।", "description_pa": "ਟਮਾਟਰ ਵਿੱਚ ਸੈਪਟੋਰੀਆ ਪੱਤੀ ਧੱਬਾ ਹੁੰਦਾ ਹੈ।", "severity": "medium"},
    {"id": "tomato_spider_mites", "class_index": 36, "name_en": "Spider Mites (Two-spotted)", "name_hi": "मकड़ी घुन", "name_pa": "ਮੱਕੜੀ ਘੁਣ", "crop_en": "Tomato", "crop_hi": "टमाटर", "crop_pa": "ਟਮਾਟਰ", "description_en": "Spider mites cause stippling and bronzing of tomato leaves. Heavy infestations lead to leaf drop and significant yield reduction.", "description_hi": "मकड़ी घुन टमाटर की पत्तियों में धब्बे और कांस्य रंग का कारण बनती है।", "description_pa": "ਮੱਕੜੀ ਘੁਣ ਟਮਾਟਰ ਦੀਆਂ ਪੱਤੀਆਂ ਵਿੱਚ ਧੱਬੇ ਬਣਾਉਂਦੀ ਹੈ।", "severity": "medium"},
]


async def init_db(db: AsyncSession) -> None:
    """
    Seed disease and treatment data into the database on first run.
    Idempotent: checks if diseases table is empty before seeding.

    Args:
        db: Async SQLAlchemy session.
    Side effects:
        Populates diseases and treatments tables.
    """
    result = await db.execute(select(Disease).limit(1))
    if result.scalars().first() is not None:
        logger.info("Database already seeded, skipping")
        return

    logger.info("Seeding database with disease and treatment data")

    # Seed fully detailed diseases
    for data in DISEASE_SEED_DATA:
        treatments = data.pop("treatments", [])
        disease = Disease(**data)
        db.add(disease)
        await db.flush()

        for t_data in treatments:
            treatment = Treatment(disease_id=disease.id, **t_data)
            db.add(treatment)

    # Seed healthy classes
    for h in HEALTHY_CLASSES:
        disease = Disease(
            id=h["id"],
            class_index=h["class_index"],
            name_en="Healthy",
            name_hi="स्वस्थ",
            name_pa="ਸਿਹਤਮੰਦ",
            crop_en=h["crop_en"],
            crop_hi=h["crop_hi"],
            crop_pa=h["crop_pa"],
            description_en=f"The {h['crop_en']} plant appears healthy with no visible disease symptoms.",
            description_hi=f"{h['crop_hi']} का पौधा स्वस्थ दिखता है, कोई बीमारी के लक्षण नहीं हैं।",
            description_pa=f"{h['crop_pa']} ਦਾ ਪੌਦਾ ਸਿਹਤਮੰਦ ਦਿਖਾਈ ਦਿੰਦਾ ਹੈ।",
            severity="low",
        )
        db.add(disease)

    # Seed remaining diseases without detailed treatments
    for r in REMAINING_DISEASES:
        disease = Disease(
            id=r["id"],
            class_index=r["class_index"],
            name_en=r["name_en"],
            name_hi=r["name_hi"],
            name_pa=r["name_pa"],
            crop_en=r["crop_en"],
            crop_hi=r["crop_hi"],
            crop_pa=r["crop_pa"],
            description_en=r["description_en"],
            description_hi=r["description_hi"],
            description_pa=r["description_pa"],
            severity=r["severity"],
        )
        db.add(disease)
        # Add default treatment for each
        treatment = Treatment(
            disease_id=disease.id,
            type="chemical",
            name_en="Consult local agricultural extension officer",
            name_hi="स्थानीय कृषि विस्तार अधिकारी से परामर्श करें",
            name_pa="ਸਥਾਨਕ ਖੇਤੀਬਾੜੀ ਵਿਸਤਾਰ ਅਧਿਕਾਰੀ ਨਾਲ ਸਲਾਹ ਕਰੋ",
            dosage="As recommended",
            schedule="Contact KVK for region-specific advice",
        )
        db.add(treatment)

    await db.commit()
    logger.info("Database seeding complete")
