import streamlit as st

# PAGE

def setup_page():

    st.set_page_config(

        page_title="Intelligent Text Processing System",

        page_icon="🧠",

        layout="wide"
    )

    st.markdown("""

<style>

.block-container {

    padding-top: 2rem;
}

/* Tabs */

button[data-baseweb="tab"] {

    font-size: 22px !important;

    font-weight: 700 !important;

    padding: 15px 25px !important;
}

/* Cards */

[data-testid="metric-container"] {

    background-color: #111827;

    border: 1px solid #1f2937;

    padding: 20px;

    border-radius: 16px;
}

/* Pipeline */

.pipeline-box {

    background-color: #111827;

    padding: 25px;

    border-radius: 16px;

    border: 1px solid #1f2937;

    margin-top: 20px;
}

/* Text area */

textarea {

    font-size: 18px !important;
}

/* Titles */

h1 {

    font-size: 60px !important;
}

h2 {

    font-size: 38px !important;
}

h3 {

    font-size: 30px !important;
}

</style>

""", unsafe_allow_html=True)

# HEADER

def show_header():

    st.markdown("""

<div style="padding-top:20px;padding-bottom:20px;">

<h1 style="
font-size:60px;
margin-bottom:5px;
">
🧠 Intelligent Text Processing System
</h1>

<p style="
font-size:24px;
color:#9ca3af;
margin-top:0;
line-height:1.6;
">

Sistema inteligente de análise,
correção e preparação automática
de texto para Inteligência Artificial.

</p>

</div>

""", unsafe_allow_html=True)

# CARDS

def show_cards():

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📄 Formatos",
            "PDF • DOCX • TXT"
        )

    with col2:

        st.metric(
            "🌍 Idiomas",
            "Deteção automática"
        )

    with col3:

        st.metric(
            "🤖 Inteligência Artificial",
            "SLM"
        )

    with col4:

        st.metric(
            "📊 Relatórios",
            "HTML • PDF"
        )

# PIPELINE

def show_pipeline():

    st.markdown("""

<div class="pipeline-box">

<h2>🔄 Pipeline Inteligente</h2>

<p style="font-size:20px; line-height:2;">

1️⃣ Upload do documento<br>

2️⃣ Extração e OCR<br>

3️⃣ Limpeza automática<br>

4️⃣ Correção ortográfica<br>

5️⃣ Deteção de idioma<br>

6️⃣ Segmentação em chunks<br>

7️⃣ Processamento pelo SLM<br>

8️⃣ Geração de relatório<br>

</p>

</div>

""", unsafe_allow_html=True)

# METRICS

def show_metrics(

    language,
    errors,
    cleaned_text
):

    st.divider()

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.info(
            f"🌍 Idioma: {language.upper()}"
        )

    with m2:

        st.warning(
            f"⚠️ Correções: {len(errors)}"
        )

    with m3:

        st.success(
            f"📝 Palavras: {len(cleaned_text.split())}"
        )

    with m4:

        st.info(
            f"🔠 Carateres: {len(cleaned_text)}"
        )

# SCORE

def show_quality_score(score):

    st.subheader(
        "📈 Qualidade do Texto"
    )

    st.progress(score)

    if score >= 90:

        st.success(
            f"Excelente qualidade ({score}%)"
        )

    elif score >= 70:

        st.warning(
            f"Boa qualidade ({score}%)"
        )

    else:

        st.error(
            f"Qualidade baixa ({score}%)"
        )