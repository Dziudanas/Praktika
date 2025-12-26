# from flask import Flask, render_template, request, jsonify
# from google import genai
# from google.genai import types
# import json

# app = Flask(__name__)

# # Konfigūracija
# API_KEY = "AIzaSyDlDgAWK1onGL3PFWf_NLuOoM1zXBBoqkA"
# client = genai.Client(api_key=API_KEY)
# MODEL_ID = "gemini-2.5-flash"

# SYSTEM_PROMPT = """
# Tu esi VILNIUS TECH humanoidas. Atsakyk į moksleivių klausimus.
# Atsakymą pateik TIK JSON formatu:
# {
#   "tekstas": "Atsakymas moksleiviui",
#   "komanda": "vaziuoti" arba "nieko",
#   "lokacija": "stendas_it", "stendas_mechanika" arba null
# }
# """

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/ask', methods=['POST'])
# def ask():
#     user_input = request.json.get('message')
#     try:
#         response = client.models.generate_content(
#             model=MODEL_ID,
#             config=types.GenerateContentConfig(
#                 system_instruction=SYSTEM_PROMPT,
#                 response_mime_type="application/json",
#                 temperature=0.3
#             ),
#             contents=user_input
#         )
#         return jsonify(json.loads(response.text))
#     except Exception as e:
#         return jsonify({"tekstas": f"Klaida: {str(e)}", "komanda": "nieko", "lokacija": None})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types
import json

app = Flask(__name__)

# --- KONFIGŪRACIJA ---
API_KEY = "AIzaSyDlDgAWK1onGL3PFWf_NLuOoM1zXBBoqkA"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"

# HTML kodas kaip kintamasis (kad nereikėtų atskiro failo testuojant)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VILNIUS TECH Humanoidas</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; padding: 50px; }
        .box { border: 2px solid #FF5A00; padding: 20px; display: inline-block; border-radius: 10px; }
        input { padding: 10px; width: 300px; }
        button { padding: 10px 20px; background: #FF5A00; color: white; border: none; cursor: pointer; }
        #log { margin-top: 20px; color: #00ff00; font-family: monospace; }
    </style>
</head>
<body>
    <div class="box">
        <h1>VILNIUS TECH ROBOTAS</h1>
        <input type="text" id="msg" placeholder="Klausk moksleivi...">
        <button onclick="ask()">KLAUSTI</button>
        <div id="resp"></div>
        <div id="log"></div>
    </div>

    <script>
        async function ask() {
            const msg = document.getElementById('msg').value;
            const log = document.getElementById('log');
            const resp = document.getElementById('resp');
            
            log.innerText = "SISTEMA: Galvojama...";
            
            const r = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const d = await r.json();
            
            resp.innerHTML = "<h3>Robotas sako:</h3>" + d.tekstas;
            log.innerText = "SISTEMA: Komanda -> " + d.komanda + " [" + d.lokacija + "]";
        }
    </script>
</body>
</html>
"""



PROMPTAS_ROBOTUI = """
Vaidmuo: Tu esi specializuotas VILNIUS TECH universiteto humanoidas-konsultantas.
Tikslas: Teikti informaciją TIK apie VILNIUS TECH (studijas, fakultetus, stojimo tvarką, lokacijas).

Griežtos taisyklės:
1. Jei vartotojas klausia apie bet ką, kas nesusiję su VILNIUS TECH (pvz., apie orus, maistą, kitus universitetus, matematiką ne kontekste), privalai mandagiai atsisakyti atsakyti.
2. Atsakymas visada turi būti TIK JSON formatu.
3. Jei klausimas nesusijęs, lauke 'tekstas' parašyk: "Apgailestauju, aš esu VILNIUS TECH asistentas ir galiu padėti tik su šio universiteto studijomis susijusiais klausimais."

Žinių bazė:
- Fakultetai: Mechanikos, Elektronikos, Statybos, Transporto inžinerijos, Architektūros, Verslo vadybos, Fundamentinių mokslų, Kūrybinių industrijų, Antano Gustaičio aviacijos institutas.
- Lokacijos: Centriniai rūmai (Saulėtekio al. 11), Mechanikos/Transporto (J. Basanavičiaus g. 28).
- Stojimai: per LAMA BPO, pagrindinis reikalavimas – valstybiniai egzaminai.

JSON struktūra:
{
  "tekstas": "Tavo atsakymas čia",
  "komanda": "vaziuoti" arba "nieko",
  "lokacija": "atitinkamo fakulteto kodas arba null"
}
"""

@app.route('/')
def index():
    # Naudojame render_template_string vietoj render_template
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('message')
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=PROMPTAS_ROBOTUI,
                response_mime_type="application/json"
            ),
            contents=user_input
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        return jsonify({"tekstas": f"Klaida: {str(e)}", "komanda": "nieko", "lokacija": None})

if __name__ == '__main__':
    app.run(debug=True, port=5000)