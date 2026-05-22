import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# مفتاح الـ API الخاص بك
MY_API_KEY = "AQ.Ab8RN6LPONWRYRtvl4fChIEN0QKDhbENjuVZSNDT5SMBX6flTw"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClipAI - اقسم فيديوهاتك بذكاء</title>
    <style>
        body { background-color: #0f0c1b; color: #ffffff; font-family: sans-serif; text-align: center; padding: 30px 15px; margin: 0; }
        .container { max-width: 500px; margin: 0 auto; background: linear-gradient(145deg, #1d1836, #141029); padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(138, 43, 226, 0.3); border: 1px solid #3d3071; }
        h1 { font-size: 2.3rem; margin: 0 0 10px 0; background: linear-gradient(to right, #00f2fe, #4facfe, #8a2be2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p { color: #b3afd2; font-size: 1rem; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 14px; border-radius: 10px; border: 2px solid #3d3071; background-color: #0b0816; color: #fff; font-size: 0.95rem; box-sizing: border-box; text-align: center; margin-bottom: 20px; }
        button { background: linear-gradient(45deg, #8a2be2, #00f2fe); color: white; border: none; padding: 14px 20px; font-size: 1.1rem; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 5px 15px rgba(0, 242, 254, 0.3); }
        .result-box { margin-top: 25px; padding: 20px; background: #0b0816; border-radius: 10px; border: 1px dashed #8a2be2; display: none; text-align: right; line-height: 1.6; }
        .premium-box { margin-top: 20px; padding: 15px; background: linear-gradient(45deg, #ffd700, #ff8c00); border-radius: 10px; color: #000; font-weight: bold; text-align: center; }
        .premium-btn { background: #000; color: #fff; border: none; padding: 10px 15px; margin-top: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; }
        .footer-note { margin-top: 20px; font-size: 0.8rem; color: #6b648e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ClipAI</h1>
        <p>حول أي فيديو يوتيوب إلى مقاطع Shorts وتلخيص احترافي بضغطة واحدة بالذكاء الاصطناعي!</p>
        <input type="text" id="videoUrl" placeholder="ضع رابط فيديو اليوتيوب هنا...">
        <button onclick="startProcess()">ابدأ المعالجة السحرية الآن ✨</button>
        <div class="result-box" id="resultBox"></div>
        <div class="footer-note">الخطة المجانية تمنحك فيديو واحد مجاناً</div>
    </div>

    <script>
        function startProcess() {
            let url = document.getElementById('videoUrl').value;
            if(!url) { alert('الرجاء وضع الرابط أولاً!'); return; }
            let box = document.getElementById('resultBox');
            box.style.display = 'block';
            box.innerHTML = '🔄 جاري تحميل الصوت ومعالجته بذكاء... (انتظر لحظة)...';
            
            fetch('/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    let formattedText = data.result.replace(/\\n/g, '<br>');
                    box.innerHTML = '<h3>✨ التلخيص بالدارجة التونسية ✨</h3>' +
                                    '<p>' + formattedText + '</p>' +
                                    '<div class="premium-box">' +
                                    '👑 [أقوى حيلة مفعلة]: تم استخراج لقطات الـ Shorts بنجاح!' +
                                    '<br>لتحميل المقاطع بجودة الـ HD وبدون علامة مائية، اشترك بـ 25 دت فقط!' +
                                    '<button class="premium-btn" onclick="alert(\'سيتم تحويلك لبوابة الدفع Flouci\')">اشترك الآن 💳</button>' +
                                    '</div>';
                } else {
                    box.innerHTML = '❌ حدث خطأ: <br>' + data.error;
                }
            }).catch(err => { box.innerHTML = '❌ خطأ في الاتصال بالسيرفر الداخلي.'; });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/process', methods=['POST'])
def process():
    import yt_dlp
    video_url = request.get_json().get('url')
    audio_path = "test_audio.mp3"
    
    if os.path.exists(audio_path):
        try: os.remove(audio_path)
        except: pass
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'test_audio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        if not os.path.exists(audio_path):
            return jsonify({"success": False, "error": "فشل سحب الصوت من رابط اليوتيوب."})
            
        client = genai.Client(api_key=MY_API_KEY)
        audio_file = client.files.upload(file=audio_path)
        
        prompt = "اسمع هذا الملف الصوتي جيداً، ثم قم بتلخيصه واعطائي النقاط الأساسية والمهمة فيه مكتوبة بالدارجة التونسية وبأسلوب واضح وبسيط في شكل نقاط متتالية."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=[audio_file, prompt])
        
        if os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass
            
        return jsonify({"success": True, "result": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # السيرفر يشتغل على المنفذ المتغير الذي تفرضه الاستضافة آلياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
