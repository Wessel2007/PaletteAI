import streamlit as st
import json
import re
import io
from PIL import Image
from colorthief import ColorThief
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="PaletteAI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Fundo e tipografia geral */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0e0e14;
            color: #e8e8f0;
            font-family: 'Segoe UI', sans-serif;
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { display: none; }

        /* Título principal */
        .palette-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
        }
        .palette-subtitle {
            text-align: center;
            color: #6b6b8a;
            font-size: 1.05rem;
            margin-bottom: 2.5rem;
        }

        /* Tabs personalizadas */
        [data-testid="stTabs"] button {
            font-size: 1rem;
            font-weight: 600;
            color: #6b6b8a;
            background: transparent;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #a78bfa;
            border-bottom: 2px solid #a78bfa;
        }

        /* Bloco de cor */
        .color-card {
            border-radius: 16px;
            padding: 0;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45);
            transition: transform 0.2s, box-shadow 0.2s;
            background: #1a1a2e;
            margin-bottom: 0.5rem;
        }
        .color-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.65);
        }
        .color-swatch {
            width: 100%;
            height: 180px;
            border-radius: 16px 16px 0 0;
        }
        .color-info {
            padding: 14px 16px 12px 16px;
            background: #1a1a2e;
            border-radius: 0 0 16px 16px;
        }
        .color-name {
            font-size: 0.85rem;
            font-weight: 600;
            color: #c4c4e0;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .color-hex {
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: #e8e8f0;
            font-family: 'Courier New', monospace;
        }

        /* Botão de copiar */
        .stButton > button {
            width: 100%;
            background: #252540;
            color: #a78bfa;
            border: 1px solid #3a3a5c;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 6px 12px;
            transition: all 0.2s;
            cursor: pointer;
        }
        .stButton > button:hover {
            background: #a78bfa;
            color: #0e0e14;
            border-color: #a78bfa;
        }

        /* Input e uploader */
        [data-testid="stTextInput"] input, textarea {
            background: #1a1a2e !important;
            border: 1px solid #3a3a5c !important;
            color: #e8e8f0 !important;
            border-radius: 10px !important;
        }
        [data-testid="stFileUploader"] {
            background: #1a1a2e;
            border: 2px dashed #3a3a5c;
            border-radius: 12px;
        }

        /* Botão de gerar */
        div[data-testid="stFormSubmitButton"] > button,
        [data-testid="baseButton-secondary"] {
            background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 10px 28px !important;
            font-size: 1rem !important;
            transition: opacity 0.2s !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="baseButton-secondary"]:hover {
            opacity: 0.88 !important;
        }

        /* Divisor */
        hr { border-color: #252540; }

        /* Área de imagem preview */
        [data-testid="stImage"] img {
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.5);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def rgb_to_hex(rgb: tuple) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb).upper()


def render_palette(colors: list[dict]):
    """Renderiza blocos de cor lado a lado.

    Cada item deve ter as chaves 'hex' e 'nome'.
    """
    cols = st.columns(len(colors))
    for col, cor in zip(cols, colors):
        with col:
            hex_val = cor["hex"].upper()
            nome = cor.get("nome", "")

            st.markdown(
                f"""
                <div class="color-card">
                    <div class="color-swatch" style="background-color:{hex_val};"></div>
                    <div class="color-info">
                        <div class="color-name">{nome}</div>
                        <div class="color-hex">{hex_val}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("📋 Copiar", key=f"copy_{hex_val}_{nome}"):
                st.toast(f"✅ {hex_val} copiado!", icon="🎨")
                st.components.v1.html(
                    f"<script>navigator.clipboard.writeText('{hex_val}');</script>",
                    height=0,
                )


def extract_colors_from_image(image_bytes: bytes, n: int = 5) -> list[dict]:
    buf = io.BytesIO(image_bytes)
    ct = ColorThief(buf)
    palette = ct.get_palette(color_count=n, quality=1)[:n]
    return [{"hex": rgb_to_hex(rgb), "nome": f"Cor {i+1}"} for i, rgb in enumerate(palette)]


def generate_palette_from_text(vibe: str, api_key: str) -> list[dict]:
    client = Groq(api_key=api_key)

    prompt = (
        f"Você é um designer de cores especialista. "
        f"Dado o clima/vibe: \"{vibe}\", crie exatamente 5 cores que representam essa atmosfera. "
        f"Responda SOMENTE com JSON válido, sem texto extra, no seguinte formato:\n"
        f"[\n"
        f"  {{\"hex\": \"#1a2b3c\", \"nome\": \"Nome Criativo\"}},\n"
        f"  ...\n"
        f"]\n"
        f"Os nomes devem ser poéticos e criativos, em português. Os hexadecimais devem ser válidos."
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()

    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        raise ValueError("A IA não retornou um JSON válido. Tente novamente.")

    colors = json.loads(json_match.group())

    validated = []
    for c in colors[:5]:
        hex_val = c.get("hex", "#000000")
        if not re.match(r"^#[0-9A-Fa-f]{6}$", hex_val):
            hex_val = "#888888"
        validated.append({"hex": hex_val, "nome": c.get("nome", "Sem Nome")})

    return validated


# ─── Layout principal ────────────────────────────────────────────────────────

st.markdown('<div class="palette-title">🎨 PaletteAI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="palette-subtitle">Gerador de paletas de cores com inteligência artificial</div>',
    unsafe_allow_html=True,
)

tab_imagem, tab_texto = st.tabs(["📷  Paleta por Imagem", "✨  Paleta por Vibe"])

# ─── Aba 1: Paleta por imagem ─────────────────────────────────────────────────
with tab_imagem:
    st.markdown("### Faça upload de uma imagem")
    st.caption("O app extrai automaticamente as 5 cores dominantes.")

    uploaded = st.file_uploader(
        "Arraste ou clique para enviar (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded:
        image_bytes = uploaded.read()
        img = Image.open(io.BytesIO(image_bytes))

        col_preview, col_palette = st.columns([1, 2], gap="large")

        with col_preview:
            st.image(img, caption="Imagem enviada", use_container_width=True)

        with col_palette:
            with st.spinner("Extraindo cores..."):
                try:
                    colors = extract_colors_from_image(image_bytes)
                    st.markdown("#### Paleta extraída")
                    render_palette(colors)
                except Exception as e:
                    st.error(f"Erro ao processar imagem: {e}")

# ─── Aba 2: Paleta por texto ──────────────────────────────────────────────────
with tab_texto:
    st.markdown("### Descreva uma vibe ou clima")
    st.caption(
        "Ex: *floresta ao entardecer*, *cyberpunk urbano*, *praia tropical ao amanhecer*"
    )

    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        groq_api_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Obtenha gratuitamente em https://console.groq.com",
        )

    vibe_input = st.text_input(
        "Vibe / Clima",
        placeholder="floresta ao entardecer",
        label_visibility="visible",
    )

    gerar = st.button("✨ Gerar Paleta", use_container_width=False)

    if gerar:
        if not groq_api_key:
            st.warning("Insira sua Groq API Key para continuar.")
        elif not vibe_input.strip():
            st.warning("Digite uma vibe antes de gerar.")
        else:
            with st.spinner(f'Criando paleta para "{vibe_input}"...'):
                try:
                    colors = generate_palette_from_text(vibe_input.strip(), groq_api_key)
                    st.markdown(f"#### Paleta: *{vibe_input}*")
                    render_palette(colors)
                except Exception as e:
                    st.error(f"Erro ao gerar paleta: {e}")
