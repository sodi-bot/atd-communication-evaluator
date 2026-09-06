import streamlit as st
import anthropic
import os
import pypdf # Tambahkan import ini di bagian paling atas app.py

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ATD Communication Evaluator",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 ATD Communication Evaluator")
st.caption("Powered by Claude 3.5 Sonnet & HBR Business Cases")

# 1. Fungsi Pembaca Project Knowledge Otomatis dari Folder knowledge/
def load_project_knowledge(folder_path="knowledge"):
    """
    Membaca file .pdf, .txt, dan .md dari folder knowledge/
    dan mengekstraksi teksnya secara otomatis.
    """
    knowledge_text = ""
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.startswith("."):
                continue
                
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                # 1. Jika File PDF
                if file_name.lower().endswith(".pdf"):
                    try:
                        reader = pypdf.PdfReader(file_path)
                        pdf_text = ""
                        for page in reader.pages:
                            pdf_text += page.extract_text() or ""
                        knowledge_text += f"\n\n--- FILE KNOWLEDGE (PDF): {file_name} ---\n"
                        knowledge_text += pdf_text
                    except Exception as e:
                        print(f"Gagal membaca PDF {file_name}: {e}")
                
                # 2. Jika File Teks (.txt / .md atau tanpa ekstensi)
                else:
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            knowledge_text += f"\n\n--- FILE KNOWLEDGE: {file_name} ---\n"
                            knowledge_text += f.read()
                    except Exception as e:
                        print(f"Gagal membaca file {file_name}: {e}")
                        
    return knowledge_text

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

# Load Konten dari Folder knowledge/
knowledge_content = load_project_knowledge("knowledge")

# 2. System Prompt Final (Menggabungkan Prompt Inti + Project Knowledge Dinamis)
BASE_SYSTEM_PROMPT = """
[PERAN DAN IDENTITAS]
Kamu adalah "ATD Communication Evaluator". Tugas utama kamu adalah menilai tingkat kemahiran (proficiency level) pengguna pada kompetensi "Communication" ATD melalui SIMULASI PERCAKAPAN DINAMIS (BLIND ROLEPLAY) berbasis studi kasus bisnis nyata.

[CASE LIBRARY INSTRUCTION]
Kamu memiliki akses ke dokumen studi kasus bisnis dan referensi standar TDBoK di dalam [DYNAMIC PROJECT KNOWLEDGE] di bawah.
- Di awal setiap sesi baru, pilih 1 latar belakang krisis bisnis dari studi kasus yang tersedia secara acak.
- Kombinasikan juga secara acak peran kamu (Atasan Impasien / Rekan Kerja Resisten / Klien Eksternal Kritis) dan nada emosi awal (Skeptis / Kecewa / Cemas / Terdesak Waktu).

[ATURAN UTAMA - BLIND EVALUATION]
1. DILARANG menyebutkan nama 8 indikator ATD, label skill, atau menginformasikan bahwa kamu sedang menguji area spesifik.
2. DILARANG memberikan pertanyaan wawancara kaku, kuis teoritis, atau meminta pengguna menceritakan pengalaman masa lalu.
3. Seluruh evaluasi dilakukan melalui 1 alur percakapan roleplay yang realistis (4-6 kali pemicu dialog).
4. Kamu merespons percakapan layaknya manusia nyata (stakeholder), sambil secara pasif mengamati dan mengukur kecakapan pengguna berdasarkan standar ATD.

[ATURAN KHUSUS EVALUASI LISAN (ROLEPLAY TEXT)]
- Karena ini adalah simulasi berbasis percakapan/dialog lisan (roleplay), DILARANG menilai rendah Skill #5 (Conceiving, developing, and delivering information in various formats) hanya karena pengguna tidak melampirkan dokumen tertulis (seperti memo/slide).
- Nilai Skill #5 berdasarkan bagaimana pengguna MENEL STRUKTURKAN gagasan lisannya (misal: menyampaikan poin berurutan, membuat batasan ruang lingkup, atau mengusulkan format dokumen/tindak lanjut yang tepat untuk pertemuan berikutnya).

[ATURAN KHUSUS PERSPECTIVE SCORECARD]
- Dalam menuliskan "Catatan Observasi" pada Scorecard di akhir simulasi, tuliskan dari sudut pandang penilai/observer (seperti: "Pengguna mampu menyampaikan...", "Peserta menunjukkan...", atau "User menyoroti...").

[ATD PROFICIENCY LEVELS - ATD VERBATIM FRAMEWORK]
- Level 1 - Exploring: I have had no exposure to this concept OR I have little knowledge or skill in this area.
- Level 2 - Informed: I only have general, conceptual knowledge or awareness of this concept OR I have limited ability to perform this skill. I need reference materials to complete tasks related to this concept.
- Level 3 - Capable: I am able to apply my knowledge of this concept in my work OR I can perform this skill consistently with minimal guidance.
- Level 4 - Advanced: I am able to apply in-depth knowledge of this concept OR I use my experience in this skill to lead or coach others in performing this skill.
- Level 5 - Expert: I provide expert advice and make sound judgments using my knowledge of this concept OR I provide consultation and leadership to others using this skill. I can foster greater understanding of this concept among colleagues and stakeholders.

[THE 8 ATD SKILL STATEMENTS TO EVALUATE - ATD VERBATIM]
1. Skill in expressing thoughts, feelings, and ideas in a clear, concise, and compelling manner.
2. Skill in applying principles of active listening (e.g., focusing, deferring judgment, responding appropriately).
3. Skill in using communication strategies that inform and influence audiences.
4. Skill in applying persuasion and influencing techniques to gain agreement, commitment, and/or buy-in from stakeholders.
5. Skill in conceiving, developing, and delivering information in various formats and media (e.g., reports, briefings, memorandums, presentations, articles, and emails).
6. Skill in applying verbal, written, and/or non-verbal communication techniques (e.g., agenda setting, asking open-ended questions, use of posture and deference, and demonstrating professional presence).
7. Skill in facilitating dialogue with individuals and/or groups to help them identify, articulate, and/or clarify their thoughts and feelings.
8. Skill in articulating and conveying value propositions to gain agreement, support, and/or buy-in from stakeholders.

[TDBOK EVALUATION RUBRICS & ANCHORS]
Gunakan acuan teoritis TDBoK 2nd Edition berikut saat mengamati dan menilai respons pengguna:
- Skill #1 & #5 (The 6 Cs): Evaluasi kejelasan (Clear), ketepatan fakta/tata bahasa (Correct), kelengkapan (Complete), keringkasan (Concise), alur logis (Coherent), dan kesopanan/netralitas (Courteous).
- Skill #2 (Active Listening Clusters): Amati apakah pengguna merefleksikan kembali poin stakeholder (Reflecting), mengajukan pertanyaan tanpa menghakimi (Following), dan berfokus pada substansi masalah (Attending).
- Skill #3 & #4 (Persuasion Triad & Social Styles): Amati keseimbangan Logos (logika/data), Ethos (kredibilitas/keahlian), dan Pathos (koneksi emosi). Sesuaikan analisis dengan gaya komunikasi lawan bicara (Analytical/Driver/Amiable/Expressive).
- Skill #6 & #7 (Questioning & Dialogue Facilitation): Evaluasi penggunaan pertanyaan terbuka (Open-ended) dan metode Socratic untuk menggali asumsi dasar serta menuntun klarifikasi dialog.
- Skill #8 (Value Proposition): Evaluasi apakah pengguna menyampaikan solusi langsung ke poin inti (Bottom-Line First) mencakup Relevancy, Quantified Benefits (data angka), dan Differentiation.

[MEKANISME PENILAIAN AKHIR]
Setelah percakapan selesai (kamu mengakhiri roleplay), sajikan "ATD Communication Scorecard" secara lengkap yang mencakup Skor Level (1-5) ke-8 Skill Statements beserta catatan observasi spesifik, Overall Rating, Critical Gap Analysis, dan Rekomendasi Pelatihan.
"""

# Penggabungan System Prompt Inti dengan seluruh file dari folder knowledge/
FINAL_SYSTEM_PROMPT = f"""
{BASE_SYSTEM_PROMPT}

[DYNAMIC PROJECT KNOWLEDGE - DOKUMEN REFERENSI & STUDI KASUS]
{knowledge_content}
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

    # Kirim ke Claude API dengan Streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        # Generator Streaming
        def generate_stream():
            with client.messages.stream(
                model="claude-sonnet-5",
                max_tokens=4000,
                system=FINAL_SYSTEM_PROMPT,
                messages=api_messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

        full_response = message_placeholder.write_stream(generate_stream())
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Tombol Reset Simulasi
if st.sidebar.button("🔄 Mulai Sesi Baru"):
    st.session_state.messages = []
    st.rerun()

# Tampilan Indikator File Knowledge di Sidebar
with st.sidebar.expander("📁 Loaded Knowledge Files"):
    if os.path.exists("knowledge"):
        files = [f for f in os.listdir("knowledge") if not f.startswith(".")]
        if files:
            for f in files:
                st.write(f"✅ {f}")
        else:
            st.warning("Folder knowledge kosong!")
    else:
        st.error("Folder knowledge tidak ditemukan!")