import streamlit as st
import requests
import time
import json
import base64
from streamlit_oauth import OAuth2Component

# ==========================================
# 1. إعدادات الصفحة (Page Config)
# ==========================================
st.set_page_config(
    page_title="Akın Yurt AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. تحميل الأسرار والإعدادات (Secrets)
# ==========================================
# يحاول قراءة الإعدادات من secrets.toml
try:
    # إعدادات Google Auth
    CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
    CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501/component/streamlit_oauth.authorize")
    
    # إعدادات الـ API الخلفي
    API_URL = st.secrets.get("API_URL", "http://localhost:8000")
    API_KEY = st.secrets.get("API_KEY", "akinyurt-secret-2025")
except FileNotFoundError:
    st.error("ملف secrets.toml مفقود! يرجى إنشاؤه داخل مجلد .streamlit")
    st.stop()

# روابط Google OAuth القياسية
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

# ==========================================
# 3. CSS وتصميم الواجهة (Custom Styling)
# ==========================================
st.markdown("""
<style>
    /* استيراد الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;600&display=swap');

    /* الخلفية والنصوص */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Inter', 'Cairo', sans-serif;
    }

    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* تحسين مظهر الرسائل */
    div[data-testid="stChatMessage"] {
        background-color: transparent;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    
    /* رسالة المستخدم */
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: transparent;
    }

    /* رسالة البوت */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: #1F242D;
        border: 1px solid #30363D;
    }

    /* حقل الإدخال */
    .stChatInput textarea {
        background-color: #21262D !important;
        color: white !important;
        border: 1px solid #30363D !important;
        border-radius: 15px !important;
    }
    .stChatInput textarea:focus {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.1) !important;
    }

    /* شاشة الدخول */
    .login-container {
        text-align: center;
        padding: 60px;
        background: #161B22;
        border-radius: 20px;
        margin-top: 50px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* الأزرار */
    div.stButton > button {
        background: linear-gradient(135deg, #238636, #2EA043);
        color: white;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: transform 0.1s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
    }

    /* حالة النظام */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .online { background-color: #238636; box-shadow: 0 0 5px #238636; }
    .offline { background-color: #DA3633; box-shadow: 0 0 5px #DA3633; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. إدارة الجلسة (Session State)
# ==========================================
if "email" not in st.session_state:
    st.session_state.email = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 5. شاشة تسجيل الدخول (Login Screen)
# ==========================================
def show_login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <h1 style="font-size: 3rem; background: linear-gradient(to right, #4A90E2, #9013FE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Akın Yurt
                </h1>
                <p style="font-size: 1.1rem; color: #A0A0A0;">Türkmen Gençlerinin Dijital Vizyonu</p>
                <hr style="border-color: #30363D; margin: 30px 0;">
                <p style="color: #888; font-size: 0.9rem;">Giriş yaparak devam edin</p>
            </div>
        """, unsafe_allow_html=True)
        
        # التحقق من وجود مفاتيح جوجل
        if not CLIENT_ID or not CLIENT_SECRET:
            st.warning("⚠️ Google Keys Missing in secrets.toml")
            # زر تجاوز للدخول كضيف (للتطوير فقط)
            if st.button("الدخول كضيف (Guest Login)", use_container_width=True):
                st.session_state.email = "guest@akinyurt.com"
                st.session_state.user_name = "Guest User"
                st.rerun()
        else:
            # مكون المصادقة
            oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)
            result = oauth2.authorize_button(
                name="Login with Google",
                icon="https://www.google.com/favicon.ico",
                redirect_uri=REDIRECT_URI,
                scope="openid email profile",
                key="google_auth",
                use_container_width=True
            )
            
            if result:
                # فك تشفير التوكن
                try:
                    id_token = result["token"]["id_token"]
                    payload = id_token.split('.')[1]
                    payload += '=' * (-len(payload) % 4)
                    decoded = json.loads(base64.b64decode(payload).decode('utf-8'))
                    
                    st.session_state.email = decoded.get("email")
                    st.session_state.user_name = decoded.get("name", "User")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login Error: {e}")

# ==========================================
# 6. واجهة الدردشة (Chat Interface)
# ==========================================
def check_server_health():
    """فحص اتصال الخادم الخلفي"""
    try:
        requests.get(f"{API_URL}/", timeout=1)
        return True
    except:
        return False

def show_chat_interface():
    is_online = check_server_health()

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.title("🦅 Akın Yurt AI")
        st.caption(f"User: {st.session_state.user_name}")
        
        # حالة النظام
        if is_online:
            st.markdown('<div style="padding:10px; background:#0d1117; border-radius:5px; border:1px solid #238636; color:#238636; font-weight:bold; text-align:center; margin-bottom:10px;"><span class="status-indicator online"></span> System Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding:10px; background:#0d1117; border-radius:5px; border:1px solid #DA3633; color:#DA3633; font-weight:bold; text-align:center; margin-bottom:10px;"><span class="status-indicator offline"></span> System Offline</div>', unsafe_allow_html=True)
            st.error("Backend API Unreachable")

        st.markdown("---")
        language = st.selectbox("Language / Dil", ["TR", "AR", "EN"])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Clear"):
                st.session_state.messages = []
                st.rerun()
        with col_btn2:
            if st.button("🚪 Logout"):
                st.session_state.email = None
                st.rerun()

    # --- منطقة الدردشة ---
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <h2 style="color: #E0E0E0;">Merhaba, {st.session_state.user_name}! 👋</h2>
            <p style="color: #888;">Akın Yurt size nasıl yardımcı olabilir?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # اقتراحات سريعة
        suggestions = ["Kimsin?", "Kerkük Kalesi tarihi", "Proje hakkında bilgi ver"]
        cols = st.columns(3)
        for i, sugg in enumerate(suggestions):
            if cols[i].button(sugg, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": sugg})
                st.rerun()

    # عرض الرسائل
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🦅" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
            if "source" in message:
                st.caption(f"📚 {message['source']}")

    # الإدخال والمعالجة
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # 1. إضافة رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. الرد
        with st.chat_message("assistant", avatar="🦅"):
            response_container = st.empty()
            
            with st.status("Thinking...", expanded=True) as status:
                if not is_online:
                    status.update(label="Connection Failed", state="error")
                    st.error("Cannot connect to Akın Yurt Server. Please check main.py or Ngrok.")
                else:
                    try:
                        # إعداد الطلب
                        payload = {
                            "query": prompt,
                            "username": st.session_state.email,
                            "language": language
                        }
                        headers = {
                            "x-api-key": API_KEY,
                            "Content-Type": "application/json"
                        }
                        
                        # الاتصال بالـ API
                        response = requests.post(
                            f"{API_URL}/api/v1/chat",
                            json=payload,
                            headers=headers,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            source = data["source"]
                            
                            status.update(label="Complete", state="complete", expanded=False)
                            
                            # تأثير الكتابة
                            full_text = ""
                            for chunk in answer.split():
                                full_text += chunk + " "
                                time.sleep(0.02)
                                response_container.markdown(full_text + "▌")
                            response_container.markdown(full_text)
                            
                            if "Knowledge Base" in source:
                                st.info(f"Source: {source}")
                            
                            st.session_state.messages.append({"role": "assistant", "content": answer, "source": source})
                        
                        else:
                            status.update(label="Server Error", state="error")
                            st.error(f"Error {response.status_code}: {response.text}")
                            
                    except Exception as e:
                        status.update(label="Error", state="error")
                        st.error(f"Connection Error: {e}")

# ==========================================
# 7. التشغيل الرئيسي (Main Loop)
# ==========================================
if __name__ == "__main__":
    if st.session_state.email:
        show_chat_interface()
    else:
        show_login_screen()
