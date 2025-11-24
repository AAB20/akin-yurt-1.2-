import streamlit as st
import requests
import time
import random

# ==========================================
# 1. إعدادات الصفحة (Page Config)
# ==========================================
st.set_page_config(
    page_title="Akın Yurt AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Akın Yurt AI\nTürkmen Gençlerinin Dijital Vizyonu."
    }
)

# ==========================================
# 2. إعدادات الاتصال (Connection Config)
# ==========================================
# محاولة قراءة الإعدادات من secrets.toml، وإذا لم توجد نستخدم القيم الافتراضية المحلية
try:
    API_URL = st.secrets.get("API_URL", "http://localhost:8000")
    API_KEY = st.secrets.get("API_KEY", "akinyurt-secret-2025")
except:
    API_URL = "http://localhost:8000"
    API_KEY = "akinyurt-secret-2025"

# ==========================================
# 3. CSS وتصميم الواجهة (Professional Styling)
# ==========================================
st.markdown("""
<style>
    /* استيراد الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Inter:wght@400;600&display=swap');

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
    
    /* رسالة البوت */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: #1F242D;
        border: 1px solid #30363D;
        border-left: 4px solid #4A90E2;
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
    
    /* مؤشرات الحالة */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .online { background-color: #238636; box-shadow: 0 0 8px #238636; }
    .offline { background-color: #DA3633; box-shadow: 0 0 8px #DA3633; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. إدارة الجلسة (Session State)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = random.randint(10000, 99999)
if "user_name" not in st.session_state:
    st.session_state.user_name = f"Guest_{st.session_state.session_id}"

# ==========================================
# 5. دالة فحص السيرفر
# ==========================================
def check_server_health():
    try:
        requests.get(f"{API_URL}/", timeout=1.5)
        return True
    except:
        return False

is_online = check_server_health()

# ==========================================
# 6. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.title("🦅 Akın Yurt AI")
    st.caption("Türkmen Gençlerinin Dijital Vizyonu")
    
    # حالة النظام
    if is_online:
        st.markdown('<div style="padding:10px; background:#0d1117; border-radius:5px; border:1px solid #238636; color:#238636; font-weight:bold; text-align:center; margin-bottom:10px;"><span class="status-dot online"></span> System Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:10px; background:#0d1117; border-radius:5px; border:1px solid #DA3633; color:#DA3633; font-weight:bold; text-align:center; margin-bottom:10px;"><span class="status-dot offline"></span> System Offline</div>', unsafe_allow_html=True)
        st.error("تأكد من تشغيل main.py")

    st.markdown("---")
    
    # إعدادات المستخدم
    new_name = st.text_input("اسم المستخدم (اختياري)", value=st.session_state.user_name)
    if new_name:
        st.session_state.user_name = new_name
        
    language = st.selectbox("Language / اللغة", ["TR", "AR", "EN"])
    
    st.markdown("### ⚙️ التحكم")
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(f"Backend: {API_URL}")

# ==========================================
# 7. واجهة الدردشة (Chat UI)
# ==========================================

# شاشة الترحيب
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 40px;">
        <h1 style="font-size: 3rem; background: linear-gradient(to right, #4A90E2, #9013FE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Merhaba, {st.session_state.user_name}!
        </h1>
        <p style="font-size: 1.2rem; color: #A0A0A0;">
            Ben Akın Yurt. Size nasıl yardımcı olabilirim?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # اقتراحات
    cols = st.columns(3)
    suggestions = ["Kimsin?", "Kerkük Tarihi", "Proje hakkında bilgi"]
    for i, prompt in enumerate(suggestions):
        if cols[i].button(prompt, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🦅" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])
        if "source" in message:
            st.caption(f"📚 {message['source']}")

# معالجة الإدخال
if prompt := st.chat_input("Mesajınızı yazın..."):
    
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # الرد من النظام
    with st.chat_message("assistant", avatar="🦅"):
        response_container = st.empty()
        
        with st.status("Thinking...", expanded=True) as status:
            if not is_online:
                status.update(label="Connection Error", state="error")
                st.error("لا يمكن الاتصال بالسيرفر المحلي (main.py).")
            else:
                try:
                    # إعداد الطلب
                    payload = {
                        "query": prompt,
                        "username": st.session_state.user_name,
                        "language": language
                    }
                    headers = {
                        "x-api-key": API_KEY,
                        "Content-Type": "application/json"
                    }
                    
                    # الاتصال بـ main.py
                    response = requests.post(
                        f"{API_URL}/api/v1/chat", # تأكد أن هذا المسار يطابق main.py
                        json=payload,
                        headers=headers,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        source = data["source"]
                        
                        status.update(label="Done", state="complete", expanded=False)
                        
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
                    st.error(f"Connection Failed: {e}")
