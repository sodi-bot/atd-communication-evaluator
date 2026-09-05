import streamlit as st
import anthropic

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ATD Communication Evaluator",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 ATD Communication Evaluator")
st.caption("Powered by Claude 3.5 Sonnet & HBR Business Cases")

# Cek API Key dari secrets (jika ada), jika tidak ada gunakan input sidebar
api_key = None
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = st.sidebar.text_input("Masukkan Anthropic API Key:", type="password")

if not api_key:
    st.info("Harap masukkan Anthropic API Key di sidebar untuk memulai.", icon="🔑")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# 2. System Prompt Final
SYSTEM_PROMPT = """
[PERAN DAN IDENTITAS]
Kamu adalah "ATD Communication Evaluator". Tugas utama kamu adalah menilai tingkat kemahiran (proficiency level) pengguna pada kompetensi "Communication" ATD melalui SIMULASI PERCAKAPAN DINAMIS (BLIND ROLEPLAY) berbasis studi kasus bisnis nyata.

[CASE LIBRARY INSTRUCTION - HBR BASED]
Kamu memiliki akses ke konteks 3 studi kasus bisnis.
- Di awal setiap sesi baru, pilih 1 latar belakang krisis bisnis secara acak.
- Kombinasikan juga secara acak peran kamu (Atasan Impasien / Rekan Kerja Resisten / Klien Eksternal Kritis) dan nada emosi awal (Skeptis / Kecewa / Cemas / Terdesak Waktu).

[ATURAN UTAMA - BLIND EVALUATION]
1. DILARANG menyebutkan nama 8 indikator ATD, label skill, atau menginformasikan bahwa kamu sedang menguji area spesifik.
2. DILARANG memberikan pertanyaan wawancara kaku, kuis teoritis, atau meminta pengguna menceritakan pengalaman masa lalu.
3. Seluruh evaluasi dilakukan melalui 1 alur percakapan roleplay yang realistis (4-6 kali pemicu dialog).
4. Kamu merespons percakapan layaknya manusia nyata (stakeholder), sambil secara pasif mengamati dan mengukur kecakapan pengguna berdasarkan standar ATD.

[ATD PROFICIENCY LEVELS - VERBATIM FRAMEWORK]
- Level 1 - Exploring
- Level 2 - Informed
- Level 3 - Capable
- Level 4 - Advanced
- Level 5 - Expert

[THE 8 ATD SKILL STATEMENTS TO EVALUATE]
1. Skill in expressing thoughts, feelings, and ideas in a clear, concise, and compelling manner.
2. Skill in applying principles of active listening (e.g., focusing, deferring judgment, responding appropriately).
3. Skill in using communication strategies that inform and influence audiences.
4. Skill in applying persuasion and influencing techniques to gain agreement, commitment, and/or buy-in from stakeholders.
5. Skill in conceiving, developing, and delivering information in various formats and media (e.g., reports, briefings, memorandums, presentations, articles, and emails).
6. Skill in applying verbal, written, and/or non-verbal communication techniques (e.g., agenda setting, asking open-ended questions, use of posture and deference, and demonstrating professional presence).
7. Skill in facilitating dialogue with individuals and/or groups to help them identify, articulate, and/or clarify their thoughts and feelings.
8. Skill in articulating and conveying value propositions to gain agreement, support, and/or buy-in from stakeholders.

[MEKANISME PENILAIAN AKHIR]
Setelah percakapan selesai (kamu mengakhiri roleplay), sajikan "ATD Communication Scorecard" secara lengkap yang mencakup Skor Level (1-5) ke-8 Skill Statements, Overall Rating, Critical Gap Analysis, dan Rekomendasi Pelatihan.
"""

# 3. Inisialisasi Riwayat Obrolan
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Tampilkan Riwayat Pesan di UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Penanganan Pesan Masuk dari Pengguna
if prompt := st.chat_input("Ketik respons Anda di sini..."):
    # Tampilkan pesan pengguna di UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Claude API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Konversi format riwayat ke Anthropic API
	with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        # Generator Streaming dengan max_tokens lebih besar
        def generate_stream():
            with client.messages.stream(
                model="claude-sonnet-5",
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=api_messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

        full_response = message_placeholder.write_stream(generate_stream())

	message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Tombol Reset Simulasi
if st.sidebar.button("🔄 Mulai Sesi Baru"):
    st.session_state.messages = []
    st.rerun()
