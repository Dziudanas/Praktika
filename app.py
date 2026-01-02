import os
import json
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Lokaliai užkrauna .env, Render platformoje naudoja sistemos kintamuosius
load_dotenv()

app = Flask(__name__)

# API raktą paimame iš Render Environment Variables
API_KEY = os.getenv("GEMINI_API_KEY")

# Patikra: Jei raktas nerastas, serveris apie tai praneš loguose
if not API_KEY:
    print("KLAIDA: GEMINI_API_KEY aplinkos kintamasis nerastas!")

client = genai.Client(api_key=API_KEY)

# Jūsų naudojamas modelis
MODEL_ID = "gemini-2.5-flash"

# HTML kodas kaip kintamasis (kad nereikėtų atskiro failo testuojant)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VILNIUS TECH Humanoidas</title>
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; height: 100vh; margin: 0; }
        .chat-container { width: 95%; max-width: 800px; background: #1e1e1e; border-radius: 12px; display: flex; flex-direction: column; height: 85vh; margin-top: 20px; border: 1px solid #333; box-shadow: 0 8px 32px rgba(0,0,0,0.8); }
        #chat-window { flex-grow: 1; overflow-y: auto; padding: 25px; display: flex; flex-direction: column; gap: 15px; }
        
        /* Žinučių burbulai */
        .message { padding: 12px 18px; border-radius: 18px; max-width: 75%; line-height: 1.5; font-size: 16px; position: relative; }
        .user { align-self: flex-end; background: #FF5A00; color: white; border-bottom-right-radius: 4px; }
        .bot { align-self: flex-start; background: #2d2d2d; color: #ffffff; border: 1px solid #444; border-bottom-left-radius: 4px; }
        
        /* Valdymas */
        .input-area { padding: 20px; background: #252525; display: flex; gap: 12px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }
        input { flex-grow: 1; padding: 14px; border-radius: 8px; border: 1px solid #444; background: #121212; color: white; outline: none; font-size: 16px; }
        input:focus { border-color: #FF5A00; }
        button { padding: 10px 25px; background: #FF5A00; color: white; border: none; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.2s; }
        button:hover { background: #e04f00; transform: translateY(-1px); }
        
        #status { font-size: 0.8em; color: #777; padding: 10px 25px; text-align: left; background: #1e1e1e; width: 100%; box-sizing: border-box; border-top: 1px solid #333; }
        h1 { color: #FF5A00; margin: 15px 0; font-weight: 800; letter-spacing: 1px; }
    </style>
</head>
<body>
    <h1>VILNIUS TECH ROBOTAS</h1>
    <div class="chat-container">
        <div id="chat-window">
            <div class="message bot">Sveiki! Esu VILNIUS TECH universiteto asistentas. Klauskite bet ko apie studijas ar fakultetus!</div>
        </div>
        <div id="status">SISTEMA: Paruošta</div>
        <div class="input-area">
            <input type="text" id="msg" placeholder="Rašykite žinutę čia..." autocomplete="off" onkeypress="if(event.key === 'Enter') ask()">
            <button onclick="ask()">SIŲSTI</button>
        </div>
    </div>

    <script>
        let chatHistory = [];

        // LIETUVIŠKO TTS FUNKCIJA
        function speakLT(text) {
            window.speechSynthesis.cancel(); // Nutraukti seną kalbą
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'lt-LT';
            utterance.rate = 1.0; // Greitis
            utterance.pitch = 1.0; // Balso aukštis

            // Ieškome geriausio lietuviško balso
            const voices = window.speechSynthesis.getVoices();
            
            // Prioritetas: Natūralūs "Microsoft Online" arba "Google" balsai
            let selectedVoice = voices.find(v => v.name.includes('Lithuania') && v.name.includes('Online'));
            
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang === 'lt-LT' || v.lang.includes('lt'));
            }

            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }

            window.speechSynthesis.speak(utterance);
        }

        async function ask() {
            const inputField = document.getElementById('msg');
            const status = document.getElementById('status');
            const userText = inputField.value.trim();
            
            if (!userText) return;

            appendMessage('user', userText);
            inputField.value = '';
            status.innerText = "SISTEMA: Galvojama...";

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: userText,
                        history: chatHistory
                    })
                });
                
                const data = await response.json();

                appendMessage('bot', data.tekstas);
                
                // Įgarsiname atsakymą
                speakLT(data.tekstas);

                status.innerText = `KOMANDA: ${data.komanda} | LOKACIJA: ${data.lokacija || 'Nėra'}`;

                // Įrašome į atmintį (JSON formatu kaip modelio atsakymą)
                chatHistory.push({role: "user", parts: [{text: userText}]});
                chatHistory.push({role: "model", parts: [{text: JSON.stringify(data)}]});

            } catch (e) {
                appendMessage('bot', "Apgailestauju, įvyko ryšio klaida.");
                status.innerText = "SISTEMA: Klaida!";
            }
        }

        function appendMessage(role, text) {
            const chatWindow = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerText = text;
            chatWindow.appendChild(div);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

        // Būtina balsų krovimui Chrome naršyklėje
        window.speechSynthesis.onvoiceschanged = () => {
            console.log("Balsai užkrauti: ", window.speechSynthesis.getVoices().length);
        };
    </script>
</body>
</html>
"""

PROMPTAS_ROBOTUI = """
Vaidmuo: Tu esi specializuotas VILNIUS TECH universiteto humanoidas-konsultantas.
Tikslas: Teikti informaciją TIK apie VILNIUS TECH (fakultetai, studijų programos, stojimo tvarka).

Griežtos taisyklės:
1. Atsakyk TIK LIETUVIŲ KALBA.
2. Atsakymas privalo būti TIK JSON formatu.
3. Jei klausimas ne apie VILNIUS TECH, mandagiai paaiškink, kad konsultuoji tik šio universiteto temomis.
4. Išlaikyk pokalbio tęstinumą.
5. Tekstą rašyk rišliai, nes jis bus skaitomas balsu (vengti simbolių kaip *, # ar ilgų sąrašų brūkšneliais).

JSON struktūra:
{
  "tekstas": "Tavo rišlus atsakymas čia",
  "komanda": "vaziuoti" arba "nieko",
  "lokacija": "fakulteto pavadinimas arba null"
}
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data.get('message')
    history = data.get('history', [])

    contents = history + [{"role": "user", "parts": [{"text": user_input}]}]

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=PROMPTAS_ROBOTUI,
                response_mime_type="application/json"
            ),
            contents=contents
        )
        
        return jsonify(json.loads(response.text))
        
    except Exception as e:
        # PAKEISTA: Grąžiname tikrąją klaidą vartotojui, kad žinotume, kas vyksta
        error_msg = str(e)
        print(f"Išsami klaida: {error_msg}")
        return jsonify({
            "tekstas": f"Sistemos klaida: {error_msg}", 
            "komanda": "nieko", 
            "lokacija": None
        })

if __name__ == '__main__':
    # SVARBU RENDER PLATFORMAI:
    # 1. Host privalo būti 0.0.0.0
    # 2. Port privalo būti paimamas iš aplinkos (os.environ)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)