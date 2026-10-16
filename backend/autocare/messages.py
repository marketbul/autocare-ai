"""Fixed user-facing texts in all three languages.

These are templates, not model output, so they are always correct and always
present (proposal §17: every diagnostic output states that the system is not a
substitute for a qualified mechanic).
"""
from __future__ import annotations

DISCLAIMER = {
    "en": "AutoCare AI is not a substitute for a qualified mechanic. If in doubt, have the vehicle inspected.",
    "ur": "آٹو کیئر اے آئی کسی مستند مکینک کا متبادل نہیں ہے۔ شک کی صورت میں گاڑی کا معائنہ کروائیں۔",
    "roman_ur": "AutoCare AI kisi mustanad mechanic ka mutabadil nahi hai. Shak ho to gaari ka muaina karwayen.",
}

NO_EVIDENCE = {
    "en": ("I could not find grounded evidence for this in your vehicle's manual or the "
           "diagnostic-code reference, so I will not guess. Please have the vehicle "
           "inspected by a qualified mechanic."),
    "ur": ("مجھے آپ کی گاڑی کے مینوئل یا تشخیصی کوڈ ریفرنس میں اس کا مستند ثبوت نہیں ملا، "
           "اس لیے میں اندازہ نہیں لگاؤں گا۔ براہِ کرم کسی مستند مکینک سے گاڑی کا معائنہ کروائیں۔"),
    "roman_ur": ("Mujhe aap ki gaari ke manual ya diagnostic code reference mein is ka mustanad "
                 "saboot nahi mila, is liye main andaza nahi lagaunga. Barah-e-karam kisi "
                 "mustanad mechanic se gaari ka muaina karwayen."),
}

CODE_NOT_FOUND = {
    "en": ("The code {codes} was not found in the diagnostic-code reference, and I will not "
           "substitute a similar code. Please check the code, or have the vehicle inspected."),
    "ur": ("کوڈ {codes} تشخیصی کوڈ ریفرنس میں نہیں ملا، اور میں اس کی جگہ ملتا جلتا کوڈ استعمال نہیں کروں گا۔ "
           "براہِ کرم کوڈ دوبارہ چیک کریں یا گاڑی کا معائنہ کروائیں۔"),
    "roman_ur": ("Code {codes} diagnostic code reference mein nahi mila, aur main is ki jagah "
                 "milta julta code istemal nahi karunga. Barah-e-karam code dobara check karein "
                 "ya gaari ka muaina karwayen."),
}

REGISTER_FIRST = {
    "en": "Please register your vehicle (make, model, variant and year) before asking a diagnostic question.",
    "ur": "تشخیصی سوال پوچھنے سے پہلے براہِ کرم اپنی گاڑی (کمپنی، ماڈل، ویریئنٹ اور سال) رجسٹر کریں۔",
    "roman_ur": "Diagnostic sawal poochne se pehle barah-e-karam apni gaari (company, model, variant aur saal) register karein.",
}

UNSUPPORTED_VEHICLE = {
    "en": "This vehicle is not supported in this release. Supported: {supported}.",
    "ur": "یہ گاڑی اس ورژن میں سپورٹڈ نہیں ہے۔ سپورٹڈ گاڑیاں: {supported}۔",
    "roman_ur": "Yeh gaari is version mein supported nahi hai. Supported: {supported}.",
}


def msg(table: dict, language: str, **kw) -> str:
    return table.get(language, table["en"]).format(**kw)
