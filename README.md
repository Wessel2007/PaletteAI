# 🎨 PaletteAI

Gerador de paletas de cores com inteligência artificial, construído com **Python + Streamlit**.

---

## Funcionalidades

### 📷 Paleta por Imagem
Faça upload de qualquer foto (JPG ou PNG) e o app extrai automaticamente as **5 cores dominantes** usando a biblioteca `colorthief`. Cada cor é exibida como um bloco visual com seu código hex e um botão para copiar.

### ✨ Paleta por Vibe
Digite uma palavra ou frase que descreva um clima ou atmosfera — como *"floresta ao entardecer"* ou *"cyberpunk urbano"* — e o app chama a **API da Groq** (modelo `llama-3.1-8b-instant`) para gerar 5 cores com nomes criativos em português que combinam com a vibe descrita.

---

## Demonstração

```
Entrada: "praia tropical ao amanhecer"

Resultado:
  #F4A261 - Areia Dourada
  #E76F51 - Coral do Alvorecer
  #2A9D8F - Turquesa das Ondas
  #264653 - Azul Oceano Profundo
  #E9C46A - Luz do Sol Nascente
```

---

## Estrutura do Projeto

```
paleta/
├── app.py            # Código principal da aplicação
├── requirements.txt  # Dependências Python
├── .env              # Variáveis de ambiente (não versionar)
└── README.md
```

---

## Pré-requisitos

- Python 3.10 ou superior
- Conta gratuita no [Groq](https://console.groq.com) para obter a API Key

---

## Instalação e execução local

```bash
# 1. Clone ou baixe o repositório
git clone https://github.com/seu-usuario/paletteai.git
cd paletteai

# 2. Crie e ative um ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure a chave da Groq
# Edite o arquivo .env e substitua o valor:
# GROQ_API_KEY=sua_chave_aqui

# 5. Execute o app
streamlit run app.py
```

O app abrirá automaticamente em `http://localhost:8501`.

> Se não tiver o `.env` configurado, o próprio app exibe um campo para inserir a chave diretamente na interface.

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|---|---|---|
| `GROQ_API_KEY` | Chave de API da Groq | Sim (para paleta por vibe) |

Obtenha sua chave gratuitamente em [console.groq.com](https://console.groq.com) → **API Keys → Create API Key**.

---

## Dependências

| Pacote | Versão mínima | Uso |
|---|---|---|
| `streamlit` | 1.35.0 | Interface web |
| `colorthief` | 0.2.1 | Extração de cores dominantes de imagens |
| `Pillow` | 10.3.0 | Processamento de imagens |
| `groq` | 0.9.0 | Cliente da API Groq (LLM) |
| `python-dotenv` | 1.0.1 | Leitura do arquivo `.env` |

---

## Deploy gratuito no Streamlit Cloud

1. Suba os arquivos `app.py` e `requirements.txt` em um repositório público no GitHub (não inclua o `.env`)
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte sua conta GitHub
3. Clique em **New app** → selecione o repositório → defina `app.py` como arquivo principal
4. Em **Advanced settings → Secrets**, adicione:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
5. Clique em **Deploy** — seu app ficará online com uma URL pública em cerca de 2 minutos

---

## Como funciona a geração por IA

O app envia o seguinte prompt à API da Groq:

```
Você é um designer de cores especialista.
Dado o clima/vibe: "{vibe}", crie exatamente 5 cores que representam essa atmosfera.
Responda SOMENTE com JSON válido, sem texto extra, no seguinte formato:
[
  {"hex": "#1a2b3c", "nome": "Nome Criativo"},
  ...
]
Os nomes devem ser poéticos e criativos, em português. Os hexadecimais devem ser válidos.
```

A resposta é validada com regex antes de ser exibida, garantindo que apenas hexadecimais válidos sejam renderizados.

---

## Tecnologias utilizadas

- [Streamlit](https://streamlit.io) — framework para apps web em Python
- [ColorThief](https://github.com/fengsp/color-thief-py) — extração de paleta de imagens
- [Groq](https://groq.com) — inferência de LLM de alta velocidade
- [Llama 3.1 8B Instant](https://console.groq.com/docs/models) — modelo de linguagem usado para geração criativa

---

## Licença

MIT — sinta-se livre para usar, modificar e distribuir.
# PaletteAI
