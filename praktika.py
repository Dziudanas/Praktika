# from google import genai
# from google.genai import types

# # 1. API konfigūracija
# API_KEY = "AIzaSyDlDgAWK1onGL3PFWf_NLuOoM1zXBBoqkA"
# client = genai.Client(api_key=API_KEY)

# # 2. Sistemos instrukcija (Humanoido "smegenys")
# # Čia apibrėžiame VILNIUS TECH kontekstą ir elgseną
# SYSTEM_PROMPT = """
# Tu esi VILNIUS TECH universiteto humanoidas-konsultantas.
# Tavo stilius: draugiškas, inovatyvus, konkretus.
# Kalba: Lietuvių.

# SVARBU: Jei moksleivis paprašo parodyti kur nors kelią arba nuvežti prie stendo, 
# savo atsakyme būtinai paminėk vietos pavadinimą.
# """

# def gauti_atsakyma(uzklausa):
#     try:
#         response = client.models.generate_content(
#         model="gemini-1.5-flash",  # Pakeista iš 2.0 į 1.5
#         config=types.GenerateContentConfig(
#         system_instruction=SYSTEM_PROMPT,
#         temperature=0.7
#     ),
#     contents=uzklausa
# )
        
#         return response.text

#     except Exception as e:
#         return f"Sistemos klaida: {str(e)}"

# # --- Pagrindinis ciklas ---
# if __name__ == "__main__":
#     print("--- VILNIUS TECH Humanoidas Aktyvuotas ---")
#     print("(Rašykite 'pabaiga', kad išjungtumėte)")
    
#     while True:
#         tekstas = input("\nMoksleivis: ")
#         if tekstas.lower() in ["pabaiga", "exit", "stop"]:
#             break
            
#         atsakymas = gauti_atsakyma(tekstas)
#         print(f"\nRobotas: {atsakymas}")




# from google import genai

# client = genai.Client(api_key="AIzaSyDlDgAWK1onGL3PFWf_NLuOoM1zXBBoqkA")

# for model in client.models.list():
#     print(f"Modelio ID: {model.name}")


import json
from google import genai
from google.genai import types

# 1. Konfigūracija
API_KEY = "AIzaSyDlDgAWK1onGL3PFWf_NLuOoM1zXBBoqkA"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"

# 2. Sistemos instrukcija su lokacijų sąrašu
SYSTEM_PROMPT = """
Tu esi VILNIUS TECH humanoidas. Atsakyk į moksleivių klausimus.
Tu gali pasiūlyti nuvežti moksleivį į šias vietas:
- 'stendas_it' (Informacinių technologijų stendas)
- 'stendas_mechanika' (Mechanikos fakulteto stendas)
- 'stendas_statyba' (Statybos inžinerijos stendas)

Atsakymą visada pateik tik JSON formatu:
{
  "tekstas": "Tavo atsakymas moksleiviui lietuviškai",
  "komanda": "vaziuoti" arba "nieko",
  "lokacija": "vietos_kodas" arba null
}
"""

def gauti_roboto_atsakyma(uzklausa):
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json", # Priverčiame Gemini grąžinti JSON
                temperature=0.3 # Mažesnė temperatūra = tikslesnis formatas
            ),
            contents=uzklausa
        )
        
        # Paverčiame tekstą į Python žodyną (dict)
        data = json.loads(response.text)
        return data

    except Exception as e:
        return {"tekstas": f"Klaida: {e}", "komanda": "nieko", "lokacija": None}

# --- Testavimo ciklas ---
if __name__ == "__main__":
    print(f"--- Humanoidas aktyvuotas ({MODEL_ID}) ---")
    
    while True:
        klausimas = input("\nMoksleivis: ")
        if klausimas.lower() in ["exit", "stop"]: break
        
        rezultatas = gauti_roboto_atsakyma(klausimas)
        
        # 1. Ką robotas sako:
        print(f"ROBOTAS SAKO: {rezultatas['tekstas']}")
        
        # 2. Ką roboto ratai daro:
        if rezultatas['komanda'] == "vaziuoti":
            print(f"SISTEMINĖ KOMANDA: Judėti į koordinates -> {rezultatas['lokacija']}")
        else:
            print("SISTEMINĖ KOMANDA: Stovėti vietoje.")