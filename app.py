import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

# =========================================================
# 1. إعدادات الاتصال (Configuration)
# =========================================================

# تحميل متغيرات البيئة (لقراءة المفتاح السري)
load_dotenv("akin-yurt.env")

# إعدادات الرابط والمفتاح
# بما أننا نعمل محلياً، نستخدم localhost
API_URL = "http://localhost:8000"
API_KEY = os.getenv("API_SECRET_KEY", "akinyurt-secret-2025") # المفتاح الافتراضي في حال عدم وجود الملف

st.set_page_config(
    page_title="Akın Yurt AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. تصميم احترافي (CSS styling like Gemini/ChatGPT)
# =========================================================
CUSTOM_CSS = """
<style>
    /* استيراد خطوط عصرية */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;600&display=swap');

    /* الخلفية العامة */
    .stApp {
        background-color: #131314; /* Gemini Dark Background */
        color: #E3E3E3;
        font-family: 'Inter', 'Cairo', sans-serif;
    }

    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20;
        border-right: 1px solid #333;
    }

    /* حقل الإدخال */
    .stChatInput textarea {
        background-color: #2D2E2F !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 16px !important;
        padding: 14px !important;
        font-size: 16px;
    }
    .stChatInput textarea:focus {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2) !important;
    }

    /* رسائل المحادثة */
    div[data-testid="stChatMessage"] {
        padding: 1.5rem 0 !important;
        background-color: transparent !important;
    }
    
    /* رسالة المساعد (Akın Yurt) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1E1F20 !important;
        border-radius: 12px;
        padding: 20px !important;
        margin-bottom: 15px;
        border: 1px solid #333;
    }

    /* الأفاتار (الصور الرمزية) */
    .stChatMessage .stAvatar {
        background-color: #4A90E2;
        color: white;
    }

    /* إخفاء عناصر Streamlit غير المرغوبة */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* عناوين */
    h1, h2, h3 { color: #E3E3E3 !important; }
    
    /* زر الاتصال */
    .status-indicator {
        padding: 8px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .online { background-color: #1E3A2F; color: #4CAF50; border: 1px solid #4CAF50; }
    .offline { background-color: #3A1E1E; color: #FF5252; border: 1px solid #FF5252; }

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================================
# 3. إدارة الجلسة (Session State)
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username" not in st.session_state:
    st.session_state.username = "Guest"

# دالة للتحقق من اتصال السيرفر
def check_server_status():
    try:
        requests.get(f"{API_URL}/", timeout=1)
        return True
    except:
        return False

is_online = check_server_status()

# =========================================================
# 4. القائمة الجانبية (Sidebar)
# =========================================================
with st.sidebar:
    st.title("🦅 Akın Yurt AI")
    st.caption("Türkmen Gençlerinin Dijital Vizyonu")
    
    # حالة السيرفر
    if is_online:
        st.markdown('<div class="status-indicator online">🟢 System Online (Local)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator offline">🔴 System Offline</div>', unsafe_allow_html=True)
        st.error("تأكد من تشغيل main.py")

    st.markdown("---")
    
    # إعدادات المستخدم
    st.session_state.username = st.text_input("اسم المستخدم", value=st.session_state.username)
    language = st.selectbox("اللغة / Dil", ["AR", "TR", "EN"])
    
    st.markdown("### ⚙️ التحكم")
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(f"Backend: {API_URL}")
    st.caption("Engine: DeepSeek-1.3B (Ollama)")

# =========================================================
# 5. واجهة الدردشة (Main Chat UI)
# =========================================================

# شاشة الترحيب
if not st.session_state.messages:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 80px; margin-bottom: 40px;">
            <h1 style="font-size: 3.5rem; background: -webkit-linear-gradient(45deg, #4A90E2, #9013FE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Akın Yurt</h1>
            <p style="font-size: 1.2rem; color: #888;">نظام ذكاء اصطناعي محلي آمن ومستقل.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # اقتراحات
        suggestions = ["من أنت؟", "حدثني عن كركوك", "Nejdet Koçak kimdir?", "لخص لي الملفات"]
        cols = st.columns(2)
        for i, sugg in enumerate(suggestions):
            if cols[i % 2].button(sugg, key=f"sugg_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": sugg})
                st.rerun()

# دالة الكتابة المتدفقة
def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.03)

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🦅"):
        st.markdown(message["content"])
        if "source" in message and message["source"] != "Akın Yurt AI":
            st.caption(f"📚 المصدر: {message['source']}")

# =========================================================
# 6. معالجة الإدخال والاتصال بالـ API
# =========================================================
if prompt := st.chat_input("أرسل رسالة..."):
    
    if not is_online:
        st.error("⚠️ لا يمكن الإرسال. السيرفر المحلي (main.py) لا يعمل!")
    else:
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # الرد من السيرفر
        with st.chat_message("assistant", avatar="🦅"):
            response_placeholder = st.empty()
            
            # حالة التفكير
            with st.status("جاري المعالجة...", expanded=True) as status:
                try:
                    status.write("🔐 التحقق من المفاتيح الأمنية...")
                    status.write("🧠 الاتصال بالمحرك العصبي (Local Engine)...")
                    
                    # تجهيز الطلب
                    payload = {
                        "query": prompt,
                        "language": language,
                        "username": st.session_state.username
                    }
                    
                    # إرسال المفتاح في Header
                    headers = {
                        "x-api-key": API_KEY,
                        "Content-Type": "application/json"
                    }
                    
                    # الاتصال الفعلي
                    start_time = time.time()
                    response = requests.post(
                        f"{API_URL}/chat", 
                        json=payload, 
                        headers=headers,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "")
                        source = data.get("source", "Unknown")
                        
                        status.update(label=f"تم (الزمن: {round(time.time() - start_time, 2)}ث)", state="complete", expanded=False)
                        
                        # عرض النص
                        response_placeholder.write_stream(stream_text(answer))
                        
                        # عرض المصدر
                        if source and "Knowledge Base" in source:
                            st.info(f"مستند إلى: {source}")
                        elif source and "Cloud Memory" in source:
                            st.success(f"من الذاكرة: {source}")
                        
                        # الحفظ
                        st.session_state.messages.append({"role": "assistant", "content": answer, "source": source})
                        
                    elif response.status_code == 403:
                        status.update(label="فشل التحقق", state="error")
                        st.error("⛔ مفتاح API غير صحيح! تأكد من ملف akin-yurt.env")
                    else:
                        status.update(label="خطأ", state="error")
                        st.error(f"خطأ في السيرفر: {response.text}")
                        
                except Exception as e:
                    status.update(label="فشل الاتصال", state="error")
                    st.error(f"حدث خطأ غير متوقع: {str(e)}")