# -*- coding: utf-8 -*-
import math
from pathlib import Path
from typing import Dict, List
import io
import pandas as pd

import streamlit as st
from datetime import date, datetime, timedelta
from PIL import Image

# ——— Autorefresh opcional (recomendado para el contador) ———
try:
    from streamlit_autorefresh import st_autorefresh
    HAVE_AUTOREFRESH = True
except Exception:
    HAVE_AUTOREFRESH = False

# =========================
# Config por país
# =========================
COUNTRY_CONFIG: Dict[str, Dict] = {
    "Perú": {
        "code": "PE",
        "currency_symbol": "S/",
        "thousands_sep": ".",
        "prices": {
                "Batido": 184,
                "Té de Hierbas": 145,
                "Aloe Concentrado": 180,
                "Beverage Mix": 159,
                "Beta Heart": 231,
                "Fibra Activa": 168,
                "Golden Beverage": 154,
                "NRG": 112,
                "Herbalifeline": 180,
                "PDM": 234,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    "Chile": {
        "code": "CL",
        "currency_symbol": "$",
        "thousands_sep": ".",
        "prices": {
            "Batido": 40377,
            "Beta Heart": 48452,
            "PDM": 51678,
            "Beverage Mix": 34943,
            "Té de Hierbas": 32300,
            "Aloe Concentrado": 42858,
            "Fibra Activa": 39503,
            "Herbalifeline": 44964,
            "NRG": 25655,
            "Golden Beverage": 44423,
        },
        "available_products": [
            "Batido","Beta Heart","PDM","Beverage Mix","Té de Hierbas",
            "Aloe Concentrado","Fibra Activa","Herbalifeline","NRG","Golden Beverage"
        ],
    },
    # ==== NUEVO: Colombia ====
    "Colombia": {
        "code": "CO",
        "currency_symbol": "$",
        "thousands_sep": ".",
        "prices": {
            "Batido": 155000,
            "Té de Hierbas": 119000,
            "Aloe Concentrado": 157000,
            "Beverage Mix": 132000,
            "Beta Heart": 176000,
            "Fibra Activa": 128000,
            "Golden Beverage": 137000,
            "NRG": 92000,
            "Herbalifeline": 162000,
            "PDM": 194000,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: España Península ====
    "España (Península)": {
        "code": "ES-PEN",
        "currency_symbol": "€",
        "thousands_sep": ".",
        "prices": {
            "Batido": 62.59,
            "Té de Hierbas": 40.71,
            "Aloe Concentrado": 54.92,
            "Beverage Mix": 51.72,
            "Beta Heart": 56.83,
            "Fibra Activa": 39.98,
            "Golden Beverage": 82.77,
            "NRG": 71.91,
            "Herbalifeline": 43.48,
            "PDM": 72.14,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: España Canarias ====
    "España (Canarias)": {
        "code": "ES-CAN",
        "currency_symbol": "€",
        "thousands_sep": ".",
        "prices": {
            "Batido": 64.75,
            "Té de Hierbas": 46.38,
            "Aloe Concentrado": 57.28,
            "Beverage Mix": 55.17,
            "Beta Heart": 60.15,
            "Fibra Activa": 42.75,
            "Golden Beverage": 84.38,
            "NRG": 73.82,
            "Herbalifeline": 46.16,
            "PDM": 72.14,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: Italia ====
    "Italia": {
        "code": "IT",
        "currency_symbol": "€",
        "thousands_sep": ".",
        "prices": {
            "Batido": 61.60,
            "Té de Hierbas": 41.11,
            "Aloe Concentrado": 54.56,
            "Beverage Mix": 48.41,
            "Beta Heart": 54.33,
            "Fibra Activa": 43.34,
            "Golden Beverage": 40.84,
            "NRG": 69.87,
            "Herbalifeline": 40.54,
            "PDM": 72.69,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: Argentina ====
    "Argentina": {
        "code": "AR",
        "currency_symbol": "$",
        "thousands_sep": ".",
        "prices": {
            "Batido": 80.124,
            "Té de Hierbas": 60.756,
            "Aloe Concentrado": 81.199,
            "Beverage Mix": 83.412,
            "Beta Heart": 114.722,
            "Fibra Activa": 80.303,
            "Golden Beverage": 68.287,
            "NRG": 49.293,
            "Herbalifeline": 90.878,
            "PDM": 133.342,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: Estados Unidos ====
    "Estados Unidos": {
        "code": "US",
        "currency_symbol": "$",
        "thousands_sep": ",",
        "prices": {
            "Batido": 72.24,
            "Té de Hierbas": 46.28,
            "Aloe Concentrado": 56.50,
            "Beverage Mix": 47.88,
            "Fibra Activa": 52.30,
            "Golden Beverage": 82.25,
            "NRG": 38.71,
            "Herbalifeline": 57.94,
            "PDM": 87.05,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: Canada ====
    "Canada": {
        "code": "CA",
        "currency_symbol": "$",
        "thousands_sep": ",",
        "prices": {
            "Batido": 71.20,
            "Té de Hierbas": 43.60,
            "Aloe Concentrado": 54.25,
            "Beverage Mix": 45.05,
            "Beta Heart": 49.90,
            "Fibra Activa": 49.90,
            "Golden Beverage": 85.20,
            "NRG": 34.80,
            "Herbalifeline": 55.90,
            "PDM": 87.50,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
    # ==== NUEVO: Mexico ====
    "Mexico": {
        "code": "MX",
        "currency_symbol": "$",
        "thousands_sep": ",",
        "prices": {
            "Batido": 893,
            "Té de Hierbas": 487,
            "Aloe Concentrado": 642,
            "Beverage Mix": 228,
            "Beta Heart": 1350,
            "Fibra Activa": 736,
            "Golden Beverage": 1271,
            "NRG": 396,
            "Herbalifeline": 887,
            "PDM": 1220,
        },
        "available_products": [
            "Batido","Té de Hierbas","Aloe Concentrado","Beverage Mix","Beta Heart",
            "Fibra Activa","Golden Beverage","NRG","Herbalifeline","PDM"
        ],
    },
}

# =========================
# Utilidades IMC
# =========================
def _imc_categoria_y_sintomas(imc: float):
    if imc is None:
        return None, ""
    if imc < 18.5:
        return "BAJO PESO", "Fatiga, fragilidad, baja masa muscular"
    elif imc < 25:
        return "PESO NORMAL", ""
    elif imc < 30:
        return "SOBREPESO", "Enfermedades digestivas, problemas de circulación en piernas, varices"
    elif imc < 35:
        return "OBESIDAD I", "Apnea del sueño, hipertensión, resistencia a la insulina"
    elif imc < 40:
        return "OBESIDAD II", "Dolor articular, hígado graso, riesgo cardiovascular"
    else:
        return "OBESIDAD III", "Riesgo cardiovascular elevado, diabetes tipo 2, problemas respiratorios"

def _imc_texto_narrativo(imc: float):
    cat, sintomas = _imc_categoria_y_sintomas(imc)
    imc_str = f"{imc:.1f}" if imc is not None else "0"
    if cat == "PESO NORMAL":
        return (f"Tu IMC es el Índice de Masa Corporal. Es la relación entre tu peso y tu tamaño. "
                f"El tuyo es de {imc_str}, eso indica que tienes PESO NORMAL y deberías sentirte con buen nivel de energía, "
                f"vitalidad y buena condición física. ¿Te sientes así?")
    else:
        return (f"Tu IMC es el Índice de Masa Corporporal. Es la relación entre tu peso y tu tamaño. "
                f"El tuyo es de {imc_str}, eso indica que tienes {cat} y podrías estar sufriendo de {sintomas}.")

# =========================
# Edad desde fecha
# =========================
def edad_desde_fecha(fecha_nac):
    if not fecha_nac:
        return None
    try:
        if isinstance(fecha_nac, str):
            fecha_nac = datetime.fromisoformat(fecha_nac).date()
        elif hasattr(fecha_nac, "year"):
            fecha_nac = date(fecha_nac.year, fecha_nac.month, fecha_nac.day)
        else:
            return None
        hoy = date.today()
        return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    except Exception:
        return None

# =========================
# Rango de grasa de referencia (CORREGIDO)
# =========================
def _rango_grasa_referencia(genero: str, edad: int):
    gen = (genero or "").strip().lower()
    tabla_mujer = [(20, 39, 21.0, 32.9), (40, 59, 23.0, 33.9), (60, 79, 24.0, 35.9)]
    tabla_hombre = [(20, 39, 8.0, 19.9), (40, 59, 11.0, 21.9), (60, 79, 13.0, 24.9)]
    tabla = tabla_mujer if gen.startswith("muj") else tabla_hombre
    try:
        e = int(edad)
    except Exception:
        e = 30
    for lo, hi, rmin, rmax in tabla:
        if lo <= e <= hi:
            return rmin, rmax
    # fallback seguro
    return tabla[0][2], tabla[0][3]

# -------------------------------------------------------------
# Config
# -------------------------------------------------------------
st.set_page_config(page_title="Evaluación de Bienestar", page_icon="🧭", layout="wide")
APP_DIR = Path(__file__).parent.resolve()

# =========================
# THEME (paleta inspirada en la plantilla Wix del enlace)
# =========================
def inject_theme():
    st.markdown("""
    <style>
      :root{
        /* Paleta: tonos cálidos crema + acentos verde salvia */
        --rd-bg-start:#FFF9F4;      /* crema muy claro */
        --rd-bg-end:#F7F3EE;        /* beige suave */
        --rd-card:#FFFFFF;
        --rd-border:#EAE6E1;
        --rd-accent:#3A6B64;        /* verde salvia principal */
        --rd-accent-2:#8BBFB5;      /* verde menta suave */
        --rd-text:#1F2A2E;          /* gris petróleo */
        --rd-muted:#6C7A7E;
        --rd-pill-bg:#EAF6F3;
        --rd-shadow:0 10px 24px rgba(20,40,40,.08);
        --rd-radius:18px;
        --rd-input-bg:#EEF4F2;      /* verde oliva muy claro */
        --rd-input-border:#D5E2DE;  /* borde suave */
      }

      /* Fondo general y tipografía */
      [data-testid="stAppViewContainer"]{
        background: linear-gradient(180deg,var(--rd-bg-start),var(--rd-bg-end)) fixed;
        color: var(--rd-text);
        font-family: "Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
      }

      /* Contenedor central más ancho */
      .block-container{ max-width: 1200px; }

      /* Sidebar */
      [data-testid="stSidebar"]{
        background: #ffffffE6;
        border-right: 1px solid var(--rd-border);
        backdrop-filter: blur(2px);
      }
      [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
        color: var(--rd-accent);
        font-weight: 800;
      }

      /* Títulos */
      h1, h2, h3{
        font-family: ui-serif, Georgia, "Times New Roman", serif !important;
        color: var(--rd-accent);
        letter-spacing:.2px;
      }
      h1{
        position: relative;
        display: inline-block;
        padding-bottom: .25rem;
      }
      h1:after{
        content:"";
        position:absolute; left:0; bottom:0;
        width: 56%;
        height: 8px;
        background: linear-gradient(90deg,var(--rd-accent-2),transparent);
        border-radius: 999px;
        opacity:.6;
      }

      /* Texto y enlaces */
      p, li, label, span, div{ color: var(--rd-text); }
      a{ color: var(--rd-accent); text-decoration: none; }
      a:hover{ text-decoration: underline; }

      /* Botones con estilo pastilla (texto siempre visible) */
      .stButton>button{
        background: var(--rd-accent) !important;
        color: #fff !important;
        padding: .75rem 1.1rem !important;
        border-radius: 999px !important;
        border: 1px solid var(--rd-accent) !important;
        box-shadow: var(--rd-shadow) !important;
        font-weight: 700 !important;
        transition: transform .03s ease, background .2s ease;
        opacity: 1 !important;
      }
      .stButton>button *, .stButton>button svg{ color:#fff !important; fill:#fff !important; opacity:1 !important; }
      .stButton>button:hover{ background:#2F5A53 !important; transform: translateY(-1px); }
      .stButton>button:focus{ outline: 3px solid var(--rd-accent-2) !important; }

      /* === NUEVO: mismo look para st.form_submit_button === */
      [data-testid="stFormSubmitter"] > div > button,
      [data-testid="baseButton-primaryFormSubmit"],
      [data-testid="baseButton-secondaryFormSubmit"]{
        background: var(--rd-accent) !important;
        color: #fff !important;
        padding: .75rem 1.1rem !important;
        border-radius: 999px !important;
        border: 1px solid var(--rd-accent) !important;
        box-shadow: var(--rd-shadow) !important;
        font-weight: 700 !important;
        transition: transform .03s ease, background .2s ease;
        opacity: 1 !important;
      }
      [data-testid="stFormSubmitter"] > div > button:hover,
      [data-testid="baseButton-primaryFormSubmit"]:hover,
      [data-testid="baseButton-secondaryFormSubmit"]:hover{
        background:#2F5A53 !important; transform: translateY(-1px);
      }
      [data-testid="stFormSubmitter"] > div > button:focus,
      [data-testid="baseButton-primaryFormSubmit"]:focus,
      [data-testid="baseButton-secondaryFormSubmit"]:focus{
        outline: 3px solid var(--rd-accent-2) !important;
      }

      /* Inputs redondeados */
      input, textarea{ border-radius: 14px !important; }
      .stSelectbox [data-baseweb="select"]{ border-radius: 14px !important; }

      /* === Campos de entrada más claros (verde oliva suave) === */
      [data-testid="stTextInput"] input,
      [data-testid="stTextArea"] textarea,
      [data-testid="stNumberInput"] input,
      [data-testid="stDateInput"] input,
      .stSelectbox [data-baseweb="select"] > div{
        background: var(--rd-input-bg) !important;
        border: 1px solid var(--rd-input-border) !important;
        color: var(--rd-text) !important;
        box-shadow: none !important;
      }
      [data-testid="stTextInput"] input::placeholder,
      [data-testid="stTextArea"] textarea::placeholder{
        color: rgba(31,42,46,.55) !important;
      }
      [data-testid="stTextInput"] input:focus,
      [data-testid="stTextArea"] textarea:focus,
      [data-testid="stNumberInput"] input:focus,
      [data-testid="stDateInput"] input:focus,
      .stSelectbox [data-baseweb="select"] > div:focus-within{
        border-color: var(--rd-accent) !important;
        outline: 2px solid var(--rd-accent-2) !important;
      }
      [data-testid="stTextInput"] input,
      [data-testid="stTextArea"] textarea{ caret-color: var(--rd-accent) !important; }

      /* === LISTA DESPLEGABLE MÁS CLARA (selectbox abierto) === */
      /* Fondo del menú (en el popover de BaseWeb) */
      .stSelectbox [data-baseweb="select"] [role="listbox"],
      [data-baseweb="popover"] [role="listbox"]{
        background: var(--rd-input-bg) !important;   /* verde claro */
        border: 1px solid var(--rd-input-border) !important;
        color: var(--rd-text) !important;
      }
      /* Opción normal */
      .stSelectbox [data-baseweb="select"] [role="option"],
      [data-baseweb="popover"] [role="option"]{
        color: var(--rd-text) !important;
        background: transparent !important;
      }
      /* Hover/selección: verde menta suave para contraste */
      .stSelectbox [data-baseweb="select"] [role="option"]:hover,
      [data-baseweb="popover"] [role="option"]:hover,
      .stSelectbox [data-baseweb="select"] [role="option"][aria-selected="true"],
      [data-baseweb="popover"] [role="option"][aria-selected="true"]{
        background: var(--rd-pill-bg) !important;    /* #EAF6F3 */
        color: var(--rd-accent) !important;
      }
      /* Borde del control cuando está abierto/enfocado */
      .stSelectbox [data-baseweb="select"] > div:focus-within{
        border-color: var(--rd-accent) !important;
        box-shadow: 0 0 0 2px var(--rd-accent-2) inset !important;
      }

      /* Tarjetas reutilizables */
      .rd-card{
        background: var(--rd-card);
        border: 1px solid var(--rd-border);
        border-radius: var(--rd-radius);
        box-shadow: var(--rd-shadow);
        padding: 16px 18px;
      }

      /* Chips / etiquetas de descuento */
      .rd-pill{ background: var(--rd-pill-bg); color: var(--rd-accent); padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700; }

      /* Tablas y contenedores */
      .stTable { border-radius: var(--rd-radius); overflow:hidden; box-shadow: var(--rd-shadow); }

      /* Divisor sutil */
      hr, .stDivider { opacity:.6; border-color: var(--rd-border) !important; }

      /* Countdown destacado */
      .rd-countdown{ background:#ffffffcc; backdrop-filter:saturate(1.2) blur(3px); padding:.6rem .9rem; display:inline-block; border:1px solid var(--rd-border); border-radius:999px; box-shadow: var(--rd-shadow); }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Helpers / Estado
# -------------------------------------------------------------
P3_FLAGS = [
    "p3_estrenimiento",
    "p3_colesterol_alto",
    "p3_baja_energia",
    "p3_dolor_muscular",
    "p3_gastritis",
    "p3_hemorroides",
    "p3_hipertension",
    "p3_dolor_articular",
    "p3_ansiedad_por_comer",
    "p3_jaquecas_migranas",
    "p3_diabetes_antecedentes_familiares",
]

def _apply_country_config(country_name: str):
    cfg = COUNTRY_CONFIG.get(country_name) or COUNTRY_CONFIG["Perú"]
    st.session_state.country_name = country_name
    st.session_state.country_code = cfg["code"]
    st.session_state.currency_symbol = cfg["currency_symbol"]
    st.session_state.thousands_sep = cfg["thousands_sep"]
    st.session_state.precios = cfg["prices"]
    st.session_state.available_products = set(cfg["available_products"])

def init_state():
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "datos" not in st.session_state:
        st.session_state.datos = {}
    if "estilo_vida" not in st.session_state:
        st.session_state.estilo_vida = {}
    if "metas" not in st.session_state:
        st.session_state.metas = {
            "perder_peso": False, "tonificar": False, "masa_muscular": False,
            "energia": False, "rendimiento": False, "salud": False, "otros": ""
        }
    if "valoracion_contactos" not in st.session_state:
        st.session_state.valoracion_contactos: List[Dict] = []
    for k in P3_FLAGS:
        st.session_state.setdefault(k, False)
    st.session_state.setdefault("precios_recomendados", {"batido_5": None, "combo": None})
    st.session_state.setdefault("combo_elegido", None)
    st.session_state.setdefault("promo_deadline", None)
    if "country_name" not in st.session_state:
        _apply_country_config("Perú")

def go(prev=False, next=False, to=None):
    if to is not None:
        st.session_state.step = to
    elif next:
        st.session_state.step = min(st.session_state.step + 1, 6)
    elif prev:
        st.session_state.step = max(st.session_state.step - 1, 1)

def ir_prev(): go(prev=True)
def ir_next(): go(next=True)

def bton_nav(id_pantalla: int | None = None):
    if id_pantalla is None:
        try:
            id_pantalla = int(st.session_state.get("step", 1))
        except Exception:
            id_pantalla = 1
    c1, c2 = st.columns([1, 1])
    with c1:
        st.button("⬅️ Anterior", key=f"prev_{id_pantalla}", on_click=ir_prev, type="primary")
    with c2:
        st.button("Siguiente ➡️", key=f"next_{id_pantalla}", on_click=ir_next, type="primary")

def imc(peso_kg: float, altura_cm: float) -> float:
    if not peso_kg or not altura_cm:
        return 0.0
    h = altura_cm / 100.0
    return round(peso_kg / (h*h), 1)

def rango_imc_texto(imc_val: float) -> str:
    if imc_val < 5.0:
        return "Delgadez III: Postración, Astenia, Adinamia, Enfermedades Degenerativas."
    if 5.0 <= imc_val <= 9.9:
        return "Delgadez II: Anorexia, Bulimia, Osteoporosis, Autoconsumo de Masa Muscular."
    if 10.0 <= imc_val <= 18.5:
        return "Delgadez I: Transtornos Digestivos, Debilidad, Fatiga Crónica, Ansiedad, Disfunción Hormonal."
    if 18.6 <= imc_val <= 24.9:
        return "PESO NORMAL: Estado Normal, Buen nivel de Energía, Vitalidad y Buena Condición Física."
    if 25.0 <= imc_val <= 29.9:
        return "Sobrepeso: Fatiga, Enfermedades Digestivas, Problemas de Circulación en Piernas, Varices."
    if 30.0 <= imc_val <= 34.0:
        return "Obesidad I: Diabetes, Hipertensión, Enfermedades Cardiovascular, Problemas Articulares."
    if 35.0 <= imc_val <= 39.9:
        return "Obesidad II: Cáncer, Angina de Pecho, Trombeflebitis, Arteriosclerosis, Embolias."
    return "Obesidad III: Falta de Aire, Apnea, Somnolencia, Trombosis Pulmonar, Úlceras."

def rango_grasa_referencia(genero: str, edad: int) -> str:
    if genero == "MUJER":
        if 16 <= edad <= 39: return "21% – 32.9%"
        if 40 <= edad <= 59: return "23% – 33.9%"
        if 60 <= edad <= 79: return "21% – 32.9%"
    else:
        if 16 <= edad <= 39: return "8.0% – 19.9%"
        if 40 <= edad <= 59: return "11% – 21.9%"
        if 60 <= edad <= 79: return "13% – 24.9%"
    return "—"

def req_hidratacion_ml(peso_kg: float) -> int:
    if not peso_kg: return 0
    return int(round((peso_kg/7.0)*250))

def req_proteina(genero:str, metas:dict, peso_kg:float) -> int:
    if not peso_kg: return 0
    if genero == "HOMBRE":
        if metas.get("masa_muscular"): mult = 2.0
        elif metas.get("rendimiento"): mult = 2.0
        elif metas.get("perder_peso"): mult = 1.6
        elif metas.get("tonificar"): mult = 1.6
        elif metas.get("energia"): mult = 1.6
        elif metas.get("salud"): mult = 1.6
        else: mult = 1.6
    else:
        if metas.get("masa_muscular"): mult = 1.8
        elif metas.get("rendimiento"): mult = 1.8
        elif metas.get("perder_peso"): mult = 1.4
        elif metas.get("tonificar"): mult = 1.4
        elif metas.get("energia"): mult = 1.4
        elif metas.get("salud"): mult = 1.4
        else: mult = 1.4
    return int(round(peso_kg * mult))

def bmr_mifflin(genero:str, peso_kg:float, altura_cm:float, edad:int) -> int:
    if genero == "HOMBRE":
        val = (10*peso_kg) + (6.25*altura_cm) - (5*edad) + 5
    else:
        val = (10*peso_kg) + (6.25*altura_cm) - (5*edad) - 161
    return int(round(val))

def comparativos_proteina(gramos:int) -> str:
    porciones_pollo_100g = gramos / 22.5
    huevos = gramos / 5.5
    return (f"{gramos} g ≈ {round(porciones_pollo_100g*100)} g de pechuga de pollo "
            f"o ≈ {huevos:.0f} huevos.")

def load_img(filename: str):
    p = APP_DIR / filename
    if p.exists():
        try: return Image.open(p)
        except Exception: return None
    return None

# =============================================================
# PRECIOS, VISUAL Y SELECCIÓN
# =============================================================
def _mon(v: float | int):
    symbol = st.session_state.get("currency_symbol", "S/")
    sep = st.session_state.get("thousands_sep", ".")
    s = f"{int(round(v)):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if sep != ".":
        s = s.replace(".", sep)
    return f"{symbol}{s}"

def _get_precios() -> Dict[str, int]:
    return st.session_state.get("precios", COUNTRY_CONFIG["Perú"]["prices"])

def _precio_sumado(items: List[str]):
    total = 0
    faltantes = []
    precios = _get_precios()
    for it in items:
        precio = precios.get(it)
        if precio is None:
            faltantes.append(it)
        else:
            total += precio
    return total, faltantes

def _chip_desc(pct:int):
    # Colores ajustados a la nueva paleta (no cambia el texto)
    return f"<span class='rd-pill'>-{pct}%</span>"

def _producto_disponible(nombre: str) -> bool:
    disp = st.session_state.get("available_products")
    return True if not disp else (nombre in disp)

# ——— NOMBRE MOSTRADO (sin afectar precios) ———
def _display_name(product: str) -> str:
    cc = st.session_state.get("country_code")
    # Canada: mapeos solicitados para pantalla 6
    if cc == "CA":
        if product == "Golden Beverage":
            return "Collagen Beauty Drink"
        if product == "NRG":
            return "LiftOff"
        if product == "Beta Heart":
            return "Fibra Activa"
    # España e Italia: mapeos solicitados
    if cc in ("ES-PEN", "ES-CAN", "IT"):
        if product == "NRG":
            return "High Protein Iced Coffee"
        if product in ("Beverage", "Beverage Mix"):
            return "PPP"
        if product == "Golden Beverage":
            # España -> Collagen Booster; Italia -> Herbalifeline
            return "Collagen Booster" if cc in ("ES-PEN", "ES-CAN") else "Herbalifeline"
    # Chile y Estados Unidos: caso especial para dolor articular
    if (
        cc in ("CL", "US")
        and st.session_state.get("p3_dolor_articular")
        and product == "Golden Beverage"
    ):
        return "Collagen Drink"
    # === NUEVO: Mexico muestra Collagen Beauty Drink en lugar de Golden Beverage (última página/listados) ===
    if cc == "MX" and product == "Golden Beverage":
        return "Collagen Beauty Drink"
    return product

def _render_card(titulo:str, items:List[str], descuento_pct:int=0, seleccionable:bool=False, key_sufijo:str=""):
    if not all(_producto_disponible(i) for i in items):
        return None

    total, faltantes = _precio_sumado(items)

    # ========= LÓGICA ESPECIAL SOLO PARA CANADÁ =========
    if st.session_state.get("country_code") == "CA" and titulo.strip() != "Batido + Chupapanza":
        # 1) Sumar $15 al paquete
        base_con_recargo = int(round(total + 15))
        # 2) Mostrar precio inflado como "regular" y el real (con recargo) como "promocional"
        if descuento_pct:
            precio_promocional = base_con_recargo  # precio real que pagará
            inflado = int(round(precio_promocional / (1 - descuento_pct/100)))
            tachado = f"<span style='text-decoration:line-through; opacity:.6; margin-right:8px'>{_mon(inflado)}</span>"
            precio_html = f"{tachado}<strong style='font-size:20px'>{_mon(precio_promocional)}</strong> {_chip_desc(descuento_pct)}"
        else:
            precio_promocional = base_con_recargo
            precio_html = f"<strong style='font-size:20px'>{_mon(precio_promocional)}</strong>"

        precio_desc = precio_promocional  # mantener compatibilidad con variables usadas abajo

    # ========= Resto de países =========
    else:
        if descuento_pct:
            # Precio real = total. Precio "regular" mostrado = total / (1 - d%)
            precio_promocional = int(round(total))
            inflado = int(round(precio_promocional / (1 - descuento_pct/100)))
            tachado = f"<span style='text-decoration:line-through; opacity:.6; margin-right:8px'>{_mon(inflado)}</span>"
            precio_html = f"{tachado}<strong style='font-size:20px'>{_mon(precio_promocional)}</strong> {_chip_desc(descuento_pct)}"
            # Texto bajo precio para Batido 5% en PE/CL/CO/ES/IT/US
            if titulo.strip().lower() in ("batido nutricional", "batido") and descuento_pct == 5:
                cc = st.session_state.get("country_code")
                if cc == "PE":
                    precio_html += " <span style='font-size:13px; opacity:.8'>(S/7.9 al dia)</span>"
                elif cc == "CL":
                    precio_html += " <span style='font-size:13px; opacity:.8'>($1.744 al dia)</span>"
                elif cc == "CO":
                    precio_html += " <span style='font-size:13px; opacity:.8'>($6.693 al dia)</span>"
                elif cc in ("ES-PEN", "ES-CAN", "IT"):
                    diario = round(precio_promocional / 22.0, 2)
                    precio_html += f" <span style='font-size:13px; opacity:.8'>(€{diario:.2f} al dia)</span>"
                elif cc == "US":
                    diario = round(precio_promocional / 30.0, 2)
                    precio_html += f" <span style='font-size:13px; opacity:.8'>(${diario:.2f} al dia)</span>"
            precio_desc = precio_promocional
        else:
            precio_desc = total
            precio_html = f"<strong style='font-size:20px'>{_mon(precio_desc)}</strong>"

    faltante_txt = ""
    if faltantes:
        faltante_txt = f"<div style='color:#b00020; font-size:12px; margin-top:6px'>Falta configurar precio: {', '.join(faltantes)}</div>"

    items_txt = " + ".join(_display_name(i) for i in items)
    st.markdown(
        f"""
        <div class='rd-card' style='margin:10px 0'>
          <div style='font-weight:800; font-size:17px; margin-bottom:4px'>{titulo}</div>
          <div style='font-size:13px; margin-bottom:8px'>{items_txt}</div>
          <div>{precio_html}</div>
          {faltante_txt}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Para coherencia con lo mostrado: precio_regular será el inflado cuando aplique,
    # y precio_final el promocional (real). Si no hay descuento, ambos son el total normal.
    if st.session_state.get("country_code") == "CA" and titulo.strip() != "Batido + Chupapanza":
        if descuento_pct:
            precio_regular_for_payload = int(round(precio_desc / (1 - descuento_pct/100)))
        else:
            precio_regular_for_payload = precio_desc
    else:
        if descuento_pct:
            precio_regular_for_payload = int(round(precio_desc / (1 - descuento_pct/100)))
        else:
            precio_regular_for_payload = precio_desc

    payload = {
        "titulo": titulo,
        "items": items,
        "precio_regular": precio_regular_for_payload,
        "descuento_pct": descuento_pct,
        "precio_final": precio_desc,
    }

    if seleccionable:
        btn_key = f"elegir_{key_sufijo or titulo.replace(' ', '_')}"
        if st.button("Elegir este", key=btn_key, use_container_width=True):
            st.session_state.combo_elegido = payload
            st.success(f"Elegiste: {titulo} — Total {_mon(precio_desc)}")
    return precio_desc

def _combos_por_flags() -> List[Dict]:
    combos = []
    ss = st.session_state
    cc = ss.get("country_code")
    if ss.get("p3_estrenimiento"):
        combos.append((f"Batido + {_display_name('Fibra Activa')}", ["Batido", "Fibra Activa"]))
    if ss.get("p3_colesterol_alto"):
        combos.append((f"Batido + {_display_name('Herbalifeline')}", ["Batido", "Herbalifeline"]))
    if ss.get("p3_baja_energia"):
        combos.append((f"Batido + {_display_name('Té de Hierbas')}", ["Batido", "Té de Hierbas"]))
    if ss.get("p3_dolor_muscular"):
        combos.append((f"Batido + {_display_name('Beverage Mix')}", ["Batido", "Beverage Mix"]))
    if ss.get("p3_gastritis"):
        combos.append((f"Batido + {_display_name('Aloe Concentrado')}", ["Batido", "Aloe Concentrado"]))
    if ss.get("p3_hemorroides"):
        combos.append(("Batido + Aloe", ["Batido", "Aloe Concentrado"]))
    if ss.get("p3_hipertension"):
        combos.append((f"Batido + {_display_name('Fibra Activa')}", ["Batido", "Fibra Activa"]))
    if ss.get("p3_dolor_articular"):
        combos.append((f"Batido + {_display_name('Golden Beverage')}", ["Batido", "Golden Beverage"]))
    if ss.get("p3_ansiedad_por_comer"):
        combos.append((f"Batido + {_display_name('PDM')}", ["Batido", "PDM"]))
    if ss.get("p3_jaquecas_migranas"):
        combos.append((f"Batido + {_display_name('NRG')}", ["Batido", "NRG"]))
    if ss.get("p3_diabetes_antecedentes_familiares"):
        combos.append((f"Batido + {_display_name('Fibra Activa')}", ["Batido", "Fibra Activa"]))
    return combos

# ------------------------------
# Cuenta regresiva (48 horas)
# ------------------------------
def _init_promo_deadline():
    if not st.session_state.promo_deadline:
        st.session_state.promo_deadline = (datetime.now() + timedelta(hours=48)).isoformat()

def _render_countdown():
    if HAVE_AUTOREFRESH:
        st_autorefresh(interval=1000, key="promo_timer_tick")
    deadline = datetime.fromisoformat(st.session_state.promo_deadline)
    restante = max(deadline - datetime.now(), timedelta(0))
    total_seg = int(restante.total_seconds())
    h, rem = divmod(total_seg, 3600)
    m, s = divmod(rem, 60)
    if total_seg > 0:
        st.markdown(f"<div class='rd-countdown'>⏳ Promoción válida por <strong>{h:02d}:{m:02d}:{s:02d}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='rd-countdown'><strong>⏳ Promoción finalizada</strong></div>", unsafe_allow_html=True)

def mostrar_opciones_pantalla6():
    st.markdown("### Opciones recomendadas")
    _render_card("Batido", ["Batido"], 5, seleccionable=True, key_sufijo="batido")
    _render_card("Batido + Te", ["Batido", "Té de Hierbas"], 10, seleccionable=True, key_sufijo="batido_te")
    _render_card(
        "Batido + Chupapanza",
        ["Batido", "Té de Hierbas", "Fibra Activa", "Aloe Concentrado"],
        10,
        seleccionable=True,
        key_sufijo="chupapanza"
    )

    if st.session_state.combo_elegido:
        e = st.session_state.combo_elegido
        st.success(
            f"Seleccionado: **{e['titulo']}** — "
            f"{_mon(e['precio_final'])} "
            f"({e['descuento_pct']}% dscto)"
        )

# ========= CORREGIDO: Sección de Personalización =========
def _render_personaliza_programa():
    st.divider()
    st.subheader("🧩 Personaliza tu programa")

    precios = _get_precios()
    disponibles = st.session_state.get("available_products") or set(precios.keys())
    productos_ordenados = [p for p in precios.keys() if p in disponibles]

    # Cabecera de tabla
    cols = st.columns([3, 2, 2])
    with cols[0]:
        st.markdown("**Producto**")
    with cols[1]:
        st.markdown("**Precio unitario**")
    with cols[2]:
        st.markdown("**Cantidad**")

    cantidades = {}
    for prod in productos_ordenados:
        c = st.columns([3, 2, 2])
        with c[0]:
            st.write(_display_name(prod))
        with c[1]:
            st.write(_mon(precios.get(prod, 0)))
        with c[2]:
            cantidades[prod] = st.selectbox(
                " ",
                options=list(range(0, 11)),
                index=0,
                key=f"custom_qty_{prod}",
                label_visibility="collapsed"
            )

    # Cálculo de totales
    total_items = sum(int(q) for q in cantidades.values())
    total_base = 0
    for prod, q in cantidades.items():
        precio_u = precios.get(prod, 0)
        total_base += int(q) * (precio_u if isinstance(precio_u, (int, float)) else 0)

    # Regla de descuento
    if total_items <= 0:
        descuento_pct = 0
    elif total_items == 1:
        descuento_pct = 5
    else:
        descuento_pct = 10

    # Recargo Canadá: +15 si hay al menos 1 ítem
    cc = st.session_state.get("country_code")
    recargo_ca = 15 if (cc == "CA" and total_items > 0) else 0

    # Precio real (promocional)
    precio_promocional = int(round(total_base + recargo_ca))

    # Precio regular “inflado” cuando hay descuento (coherente con tarjetas)
    if descuento_pct > 0:
        precio_regular_inflado = int(round(precio_promocional / (1 - descuento_pct/100)))
        html_total = (
            f"<span style='text-decoration:line-through; opacity:.6; margin-right:8px'>{_mon(precio_regular_inflado)}</span>"
            f"<strong style='font-size:20px'>{_mon(precio_promocional)}</strong> "
            f"{_chip_desc(descuento_pct)}"
        )
    else:
        html_total = f"<strong style='font-size:20px'>{_mon(precio_promocional)}</strong>"

    # Tarjeta visual
    st.markdown(
        f"""
        <div class='rd-card' style='margin:10px 0'>
          <div style='font-weight:800; font-size:17px; margin-bottom:6px'>Total del programa</div>
          <div>{html_total}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
# ========= FIN CORRECCIÓN =========

# -------------------------------------------------------------
# STEP 1 - Perfil de Bienestar
# -------------------------------------------------------------
def pantalla1():
    st.header("1) Perfil de Bienestar")
    with st.form("perfil"):
        st.subheader("Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("¿Cuál es tu nombre completo?")
            email  = st.text_input("¿Cuál es tu correo electrónico?")
            movil  = st.text_input("¿Cuál es tu número de teléfono?")
            ciudad = st.text_input("¿En que ciudad vives?")
        with col2:
            fecha_nac = st.date_input("¿Cuál es tu fecha de nacimiento?",
                                      value=date(1990,1,1), min_value=date(1900,1,1), max_value=date.today())
            genero = st.selectbox("¿Cuál es tu género?", ["HOMBRE", "MUJER"])

        st.subheader("País")
        pais = st.selectbox(
            "Selecciona tu país",
            ["Perú", "Chile", "Colombia", "España (Península)", "España (Canarias)", "Italia", "Argentina", "Estados Unidos", "Canada", "Mexico"],
            index=0,
            help="Esto ajustará los precios y la moneda en las recomendaciones."
        )

        st.subheader("Metas físicas y de bienestar")
        st.markdown("**¿Cuáles son tus metas? Puedes elegir más de una.**")
        c1, c2, c3 = st.columns(3)
        with c1:
            perder_peso   = st.checkbox("Perder Peso")
            tonificar     = st.checkbox("Tonificar / Bajar Grasa")
            masa_muscular = st.checkbox("Aumentar Masa Muscular")
        with c2:
            energia      = st.checkbox("Aumentar Energía")
            rendimiento  = st.checkbox("Mejorar Rendimiento Físico")
            salud        = st.checkbox("Mejorar Salud")
        with c3:
            otros = st.text_input("Otros")

        st.subheader("Análisis de Nutrición y Salud")
        c1, c2 = st.columns(2)
        with c1:
            horarios     = st.text_input("¿A qué hora despiertas y a qué hora te vas a dormir?")
            desayuno_h   = st.text_input("¿Tomas desayuno todos los días? ¿A qué hora?")
            que_desayunas = st.text_input("¿Qué sueles desayunar?")
        with c2:
            meriendas     = st.text_input("¿Comes entre comidas? ¿Qué sueles comer?")
            porciones     = st.text_input("Cuantas porciones de frutas y verduras comes al dia?")
            comer_noche   = st.text_input("Tiendes a comer de más por las noches?")
            reto          = st.text_input("Cuál es tu mayor reto respecto a la comida?")
            agua8         = st.text_input("¿Tomas por lo menos 8 vasos de agua al dia?")
            alcohol       = st.text_input("¿Tomas bebidas alcohólicas? ¿Cuántas veces al mes?")

        enviado = st.form_submit_button("Guardar y continuar ➡️", use_container_width=True, type="primary")
        if enviado:
            st.session_state.datos.update({
                "nombre": nombre, "email": email, "movil": movil, "ciudad": ciudad,
                "fecha_nac": str(fecha_nac), "genero": genero
            })
            _apply_country_config(pais)
            st.session_state.metas.update({
                "perder_peso": perder_peso, "tonificar": tonificar, "masa_muscular": masa_muscular,
                "energia": energia, "rendimiento": rendimiento, "salud": salud, "otros": otros
            })
            st.session_state.estilo_vida.update({
                "horarios": horarios,
                "desayuno_h": desayuno_h,
                "que_desayunas": que_desayunas,
                "meriendas": meriendas,
                "porciones": porciones,
                "comer_noche": comer_noche,
                "reto": reto,
                "agua8_p1": agua8,
                "alcohol_mes": alcohol
            })
            go(next=True)

# -------------------------------------------------------------
# STEP 2 - Evaluación de Composición Corporal
# -------------------------------------------------------------
def _calcular_edad(fecha_iso: str) -> int:
    try:
        anio = int(str(fecha_iso).split("-")[0])
    except Exception:
        return 30
    return max(16, min(79, date.today().year - anio))

def pantalla2():
    st.header("2) Evaluación de Composición Corporal")

    col = st.columns([2,1,1])
    with col[1]:
        peso_lb = st.number_input("Peso (lb)", min_value=0.0, max_value=900.0, step=0.1,
                                  value=float(st.session_state.get("peso_lb_value", 0.0)))
        if st.button("Convertir a kilogramos"):
            if peso_lb and peso_lb > 0:
                st.session_state["peso_kg_value"] = round(peso_lb * 0.45359237, 2)
                st.session_state["peso_lb_value"]  = float(peso_lb)
                st.success(f"{peso_lb} lb = {st.session_state['peso_kg_value']} kg")

    with col[0]:
        altura_cm = st.number_input("Altura (cm)", min_value=50, max_value=250, step=1,
                                    value=max(50, min(250, int(st.session_state.datos.get("altura_cm", 170)))))
        st.session_state.datos["altura_cm"] = altura_cm
        default_kg = float(st.session_state.get("peso_kg_value", st.session_state.datos.get("peso_kg", 0) or 0))
        peso_kg = st.number_input("Peso (kg)", min_value=0.0, max_value=400.0, step=0.1,
                                  value=float(min(400.0, max(0.0, default_kg))), key="peso_kg_input")
        st.caption("Tip: si tienes libras, usa el conversor para pasar a kg.")
    with col[2]:
        st.write(" ")
        grasa_pct = st.slider("¿Selecciona el % de grasa que más se parece?", 8, 45, 20)

    st.write("### ¿Cuál consideras que es tu % de grasa según la imagen?")
    img_local = load_img("imagen_grasa_corporal.png") or load_img("grasa_ref.png")
    uploaded = st.file_uploader("Sube una imagen de referencia (opcional)", type=["png","jpg","jpeg"])
    if uploaded is not None:
        try:
            img_local = Image.open(uploaded)
        except Exception:
            st.warning("No pude abrir la imagen subida.")
    if img_local:
        st.image(img_local, use_container_width=True)
    else:
        st.caption("Coloca 'imagen_grasa_corporal.png' o 'grasa_ref.png' en esta misma carpeta para mostrar una guía visual.")

    st.divider()
    st.subheader("Resultados")
    st.session_state.datos["altura_cm"] = altura_cm
    st.session_state.datos["peso_kg"]   = peso_kg
    st.session_state.datos["grasa_pct"] = grasa_pct

    edad   = _calcular_edad(st.session_state.datos.get("fecha_nac"))
    genero = st.session_state.datos.get("genero", "HOMBRE")

    imc_val = imc(peso_kg, altura_cm)

    datos = st.session_state.get('datos', {})
    genero_ref = (datos.get('genero') or 'Hombre')
    fecha_nac  = (datos.get('fecha_nac'))
    edad_ref   = edad_desde_fecha(fecha_nac) or int(datos.get('edad', 30))
    rmin, rmax = _rango_grasa_referencia(genero_ref, edad_ref)

    agua_ml = req_hidratacion_ml(peso_kg)
    prote_g = req_proteina(genero, st.session_state.metas, peso_kg)
    bmr     = bmr_mifflin(genero, peso_kg, altura_cm, edad)

    meta_masa = st.session_state.metas.get("masa_muscular", False)
    objetivo_kcal = bmr + 250 if meta_masa else bmr - 250

    st.write("En base a los datos introducidos, la aplicación arroja los siguientes resultados:")

    if 18.6 <= imc_val <= 24.9:
        st.write(
            f"Tu IMC, Índice de Masa Corporal, es la relación entre tu peso y tu estatura. "
            f"El tuyo es de {imc_val:.1f}, eso indica que tienes PESO NORMAL lo que significa que deberías tener buena condición física, "
            f"vitalidad y buen nivel de energía, ¿Te sientes así? . Como referencia, el IMC ideal es de 18.6 a 24.9."
        )
    else:
        st.write(
            f"Tu IMC, **Índice de Masa Corporal**, es la relación entre tu peso y tu estatura. "
            f"El tuyo es de **{imc_val:.1f}**, eso indica que tienes **{_imc_categoria_y_sintomas(imc_val)[0]}** "
            f"y eres propenso a **{_imc_categoria_y_sintomas(imc_val)[1] or '—'}**. "
            f"Como referencia, el IMC ideal es de 18.6 a 24.9."
        )

    genero_pal = "mujer" if str(genero).strip().upper().startswith("M") else "hombre"
    articulo = "Una" if genero_pal == "mujer" else "Un"
    st.write(
        f"Sobre tu % de grasa. {articulo} {genero_pal} de {edad_ref} años como tú tiene "
        f"**{rmin:.1f} % de grasa en el mejor de los casos y {rmax:.1f} % en el peor de los casos. "
        f"Tú tienes {grasa_pct}%**"
    )

    st.write(f"Respecto a tu **hidratación**, tu requerimiento es de **{agua_ml:,} ml/día.** "
                f"(Alcanzar tu requerimiento de hidratación facilita el tránsito intestinal, favorece la absorción de nutrientes y mantiene la piel firme.)" 
    )

    if objetivo_kcal < 1200:
        st.write(
            f"El resultado de metabolismo en reposo es de {bmr:,} y para alcanzar tu objetivo "
            f"se recomienda una ingesta diaria de 1,200 calorías. "
            f"(No exceder tu requerimiento de calorías diarias te permite mantener un peso saludable.)"
        )
    else:
        st.write(
            f"El resultado de metabolismo en reposo es de {bmr:,} y para alcanzar tu objetivo "
            f"**se recomienda una ingesta diaria de {objetivo_kcal:,} calorías.** "
            f"(No exceder tu requerimiento de calorías diarias te permite mantener un peso saludable.)"
        )

    pollo_g = int(round((prote_g / 22.5) * 100))
    huevos_n = int(round(prote_g / 5.5))
    st.write(
        f"Tu **requerimiento de proteína** según el objetivo que te has propuesto es de **{prote_g} gramos al día.** "
        f"Como referencia, esto equivale a {pollo_g} g de pechuga de pollo o {huevos_n} huevos. "
        f"(Alcanzar tu requerimiento de proteína diario te permite preservar músculo durante la perdida de peso, evitando la flacidez.)"
    )

    bton_nav()

# -------------------------------------------------------------
# STEP 3 - Estilo de Vida y Objetivos
# -------------------------------------------------------------
def pantalla3():
    st.header("3) Evaluación de Estilo de Vida")

    st.subheader("Hábitos y energía")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("¿En qué momento del día sientes menos energía?", key="ev_menos_energia")
        st.text_input("¿Practicas actividad física al menos 3 veces/semana?", key="ev_actividad")
        st.text_input("¿Has intentado algo antes para verte/estar mejor? (Gym, Dieta, App, Otros)", key="ev_intentos")
        st.text_input("¿Qué es lo que más se te complica? (Constancia, Alimentación, Motivación, Otros)", key="ev_complica")
        st.text_input("¿Consideras que cuidar de ti es una prioridad?", key="ev_prioridad_personal")
    with c2:
        st.write("Presentas alguna de las siguientes condiciones?")
        cols = st.columns(2)
        with cols[0]:
            estre       = st.checkbox("¿Estreñimiento?")
            colesterol  = st.checkbox("¿Colesterol Alto?")
            baja_ene    = st.checkbox("¿Baja Energía?")
            dolor_musc  = st.checkbox("¿Dolor Muscular?")
            gastritis   = st.checkbox("¿Gastritis?")
            hemorroides = st.checkbox("¿Hemorroides?")
        with cols[1]:
            hta         = st.checkbox("¿Hipertensión?")
            dolor_art   = st.checkbox("¿Dolor Articular?")
            ansiedad    = st.checkbox("¿Ansiedad por comer?")
            jaquecas    = st.checkbox("¿Jaquecas / Migrañas?")
            diabetes_fam= st.checkbox("Diabetes (antecedentes familiares)")

    st.session_state.p3_estrenimiento                      = bool(estre)
    st.session_state.p3_colesterol_alto                    = bool(colesterol)
    st.session_state.p3_baja_energia                       = bool(baja_ene)
    st.session_state.p3_dolor_muscular                     = bool(dolor_musc)
    st.session_state.p3_gastritis                          = bool(gastritis)
    st.session_state.p3_hemorroides                        = bool(hemorroides)
    st.session_state.p3_hipertension                       = bool(hta)
    st.session_state.p3_dolor_articular                    = bool(dolor_art)
    st.session_state.p3_ansiedad_por_comer                 = bool(ansiedad)
    st.session_state.p3_jaquecas_migranas                  = bool(jaquecas)
    st.session_state.p3_diabetes_antecedentes_familiares   = bool(diabetes_fam)

    st.subheader("Objetivos")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("¿Qué talla te gustaría ser?", key="obj_talla")
        st.text_input("¿Qué partes del cuerpo te gustaría mejorar?", key="obj_partes")
        st.text_input("¿Qué tienes en tu ropero que podamos usar como meta?", key="obj_ropero")
    with c2:
        st.text_input("¿Cómo te beneficia alcanzar tu meta?", key="obj_beneficio")
        st.text_input("¿Qué eventos tienes en los próximos 3 o 6 meses?", key="obj_eventos")
        st.text_input("Del 1 al 10, ¿cual es tu nivel de compromiso en alcanzar una mejor versión de ti?", key="obj_compromiso")

    st.subheader("Análisis de presupuesto")
    col = st.columns(4)
    cur = st.session_state.get("currency_symbol", "S/")
    with col[0]:
        st.number_input(f"Cuanto gastas diariamente en tu comida? ({cur}.)", min_value=0.0, step=0.1, key="presu_comida")
    with col[1]:
        st.number_input(f"Cuanto gastas diariamente en postres, snacks, dulces, etc? ({cur}.)", min_value=0.0, step=0.1, key="presu_cafe")
    with col[2]:
        st.number_input(f"Cuanto gastas a la semana en bebidas? ({cur}.)", min_value=0.0, step=0.1, key="presu_alcohol")
    with col[3]:
        st.number_input(f"Cuanto gastas a la semana en deliveries/salidas a comer? ({cur}.)", min_value=0.0, step=0.1, key="presu_deliveries")

    prom_diario = round((
        float(st.session_state.get("presu_comida", 0.0)) +
        float(st.session_state.get("presu_cafe", 0.0)) +
        (float(st.session_state.get("presu_alcohol", 0.0))/7.0) +
        (float(st.session_state.get("presu_deliveries", 0.0))/7.0)
    ), 2)

    st.write(f"La aplicación nos arroja que tu promedio de gastos diarios es de {cur} {prom_diario:.2f}.")
    st.text_input(
        "¿Consideras valioso optimizar tu presupuesto y darle prioridad a comidas y bebidas que aporten a tu bienestar y objetivos?",
        key="ev_valora_optimizar"
    )

    st.write("Hasta aqui, ¿Que te parece la información que has recibido en esta evaluación?")

    st.session_state.estilo_vida.update({
        "ev_menos_energia":      st.session_state.get("ev_menos_energia", ""),
        "ev_actividad":          st.session_state.get("ev_actividad", ""),
        "ev_intentos":           st.session_state.get("ev_intentos", ""),
        "ev_complica":           st.session_state.get("ev_complica", ""),
        "ev_prioridad_personal": st.session_state.get("ev_prioridad_personal",""),
        "ev_valora_optimizar":   st.session_state.get("ev_valora_optimizar",""),
        "presu_comida":          st.session_state.get("presu_comida", 0.0),
        "presu_cafe":            st.session_state.get("presu_cafe", 0.0),
        "presu_alcohol":         st.session_state.get("presu_alcohol", 0.0),
        "presu_deliveries":      st.session_state.get("presu_deliveries", 0.0),
    })
    st.session_state.metas.update({
        "obj_talla":      st.session_state.get("obj_talla",""),
        "obj_partes":     st.session_state.get("obj_partes",""),
        "obj_ropero":     st.session_state.get("obj_ropero",""),
        "obj_beneficio":  st.session_state.get("obj_beneficio",""),
        "obj_eventos":    st.session_state.get("obj_eventos",""),
        "obj_compromiso": st.session_state.get("obj_compromiso",""),
    })

    bton_nav()

# -------------------------------------------------------------
# STEP 4 - Valoración de Servicio
# -------------------------------------------------------------
def emoji_y_texto(n):
    if n <= 0: return "😡", "PÉSIMO"
    if n == 1: return "😠", "NO ME GUSTÓ"
    if n == 2: return "😐", "ME GUSTÓ POCO"
    if n == 3: return "🙂", "ME GUSTÓ"
    if n == 4: return "😁", "ME GUSTÓ MUCHO"
    return "🤩", "ME ENCANTÓ"

def pantalla4():
    st.header("4) Valoración de Servicio")
    st.write("La empresa valora la calidad de mi servicio según la cantidad de personas a las cuales **les quieres regalar la misma evaluación**. 1 persona significa que no te gusto y 5 personas significa que te encantó. Entonces...")

    if "valoracion_contactos" not in st.session_state:
        st.session_state.valoracion_contactos = []

    with st.form("add_ref"):
        cols = st.columns([2,1,1,1])
        with cols[0]:
            nombre   = st.text_input("¿A quién te gustaría regalarle esta evaluación?")
        with cols[1]:
            telefono = st.text_input("¿Cuál es su número de teléfono?")
        with cols[2]:
            distrito = st.text_input("¿Distrito?")
        with cols[3]:
            relacion = st.text_input("¿Qué relación tienen?")
        if st.form_submit_button("Agregar") and nombre:
            st.session_state.valoracion_contactos.append({
                "nombre": nombre, "telefono": telefono, "distrito": distrito, "relacion": relacion
            })

    if st.session_state.valoracion_contactos:
        st.table(st.session_state.valoracion_contactos)

    n = min(len(st.session_state.valoracion_contactos), 5)
    cara, texto = emoji_y_texto(n)
    st.markdown(f"### {cara}  {texto}")

    st.divider()
    st.write("Muchas gracias por tu ayuda, con ello concluimos la evaluación. Antes de despedirnos **¿Te gustaría que te explique cómo, a través de la comunidad, podemos ayudarte a alcanzar los objetivos que te has propuesto?**")

    bton_nav()

# -------------------------------------------------------------
# STEP 5 - Quiénes somos
# -------------------------------------------------------------
def show_img(filename: str, caption: str = ""):
    p = (APP_DIR / filename)
    if p.exists():
        try:
            img = Image.open(p)
            st.image(img, caption=caption if caption else None, use_container_width=True)
        except Exception as e:
            st.warning(f"No pude abrir '{filename}': {e}")
    else:
        st.warning(f"(Falta imagen: {filename})")

def pantalla5():
    st.header("5) Quiénes somos")
    st.write(
        "Somos **Fitclub**, una comunidad que educa a las personas en hábitos saludables de vida para que puedan alcanzar resultados "
        "de bienestar y puesta en forma, y sostenerlos para siempre.\n\n"
        "Contamos con una comunidad con más de 10,000 personas con resultados más allá de sus expectativas iniciales. "
        "A continuación te voy a mostrar algunos testimonios de nuestra comunidad."
    )
    st.subheader("Testimonios")

    st.markdown("""
        <style>
        .testi-title{ font-weight: 800; font-size: 1.2rem; margin: 8px 0 2px 0; }
        .testi-box{ margin-bottom: 18px; }
        </style>
    """, unsafe_allow_html=True)

    testimonios = [
        ("jessiyroi.jpg","Jessi y Roi son papás de 3 niños",
         ["El aumentó 8kg de masa muscular y ella controló 14kg post parto en 3 meses",
          "Lo que más valoran es la energía que tienen a diario para jugar y disfrutar de sus hijos."]),
        ("alexisylyn.jpg","Alexis y Lyn — Recomposición corporal",
         ["Ambos pesan lo mismo en ambas fotos. El 74 y ella 60kg.",
          "Ambos lograron una mejora notable en el tono muscular y pérdida de grasa."]),
        ("nicolasyscarlett.jpg","Nicolás y Scarlett jovenes de 18 años",
         ["Ambos aumentaron peso en masa muscular. El 20 kilos y ella 14."]),
        ("wagnerysonia.jpg","Wagner y Sonia — Tercera edad",
         ["Ambos empezaron el programa con más de 60 años, con dolores de rodillas y probelmas de salud. Los médicos solo argumentaban que eran problemas propios de la edad.",
          "Controlaron peso, mejoraron su salud y se llenaron de energía."]),
        ("mayraymariaantonieta.jpg","Mayra y María Antonieta — Hipotiroidismo",
         ["Ambas pensaban que debido a su condición no podían tener resultados. Mayra controló 20 kg y María Antonieta 15."]),
        ("reynaldoyandreina.jpg","Reynaldo y Andreina — Prediabéticos y papás de 4",
         ["Vivían a dietas sin tener resultados sostenibles. Perdían peso y lo recuperaban. Él controló 25 kg y ella 15 kg después de su última cesárea de mellizos"]),
        ("aldoycristina.jpg","Aldo y Cristina — Sin tiempo",
         ["Aldo, arquitecto, se amanecía trabajando en la oficina. Cristina, médico, con turnos de 24 a 48 horas.  Ambos con una alimentación muy desordenada. Él controló 25 kg y ella 12 kg."]),
    ]

    for fname, titulo, bullets in testimonios:
        st.divider()
        show_img(fname)
        st.markdown(f"<div class='testi-box'><div class='testi-title'>{titulo}</div></div>", unsafe_allow_html=True)
        for txt in bullets:
            st.markdown(f"- {txt}")
        st.write("")

    bton_nav()

# =========================
# Utilidad: construir Excel
# =========================
def _excel_bytes():
    d = st.session_state.get("datos", {})
    e = st.session_state.get("estilo_vida", {})
    m = st.session_state.get("metas", {})
    refs = st.session_state.get("valoracion_contactos", []) or []
    combo = st.session_state.get("combo_elegido")

    altura_cm = d.get("altura_cm")
    peso_kg   = d.get("peso_kg")
    grasa_pct = d.get("grasa_pct")
    edad_calc = edad_desde_fecha(d.get("fecha_nac")) or 0
    genero    = d.get("genero") or "HOMBRE"
    imc_val   = imc(peso_kg or 0, altura_cm or 0)
    agua_ml   = req_hidratacion_ml(peso_kg or 0)
    prote_g   = req_proteina(genero, m, peso_kg or 0)
    bmr_val   = bmr_mifflin(genero, peso_kg or 0, altura_cm or 0, max(edad_calc, 16))
    objetivo_kcal = m.get("masa_muscular") and (bmr_val + 250) or (bmr_val - 250)

    cur = st.session_state.get("currency_symbol", "S/")
    perfil = [
        ("¿Cuál es tu nombre completo?", d.get("nombre","")),
        ("¿Cuál es tu correo electrónico?", d.get("email","")),
        ("¿Cuál es su número de teléfono?", d.get("movil","")),
        ("¿En que ciudad vives?", d.get("ciudad","")),
        ("¿Cuál es tu fecha de nacimiento?", d.get("fecha_nac","")),
        ("¿Cuál es tu género?", d.get("genero","")),
        ("País seleccionado", st.session_state.get("country_name","Perú")),
        ("Altura (cm)", altura_cm),
        ("Peso (kg)", peso_kg),
        ("% de grasa estimado", grasa_pct),
    ]
    estilo = [
        ("¿A qué hora despiertas y a qué hora te vas a dormir?", e.get("horarios","")),
        ("¿Tomas desayuno todos los días? ¿A qué hora?", e.get("desayuno_h","")),
        ("¿Qué sueles desayunar?", e.get("que_desayunas","")),
        ("¿Comes entre comidas? ¿Qué sueles comer?", e.get("meriendas","")),
        ("Cuantas porciones de frutas y verduras comes al dia?", e.get("porciones","")),
        ("Tiendes a comer de más por las noches?", e.get("comer_noche","")),
        ("Cuál es tu mayor reto respecto a la comida?", e.get("reto","")),
        ("¿Tomas por lo menos 8 vasos de agua al dia?", e.get("agua8_p1","")),
        ("¿Tomas bebidas alcohólicas? ¿Cuántas veces al mes?", e.get("alcohol_mes","")),
        ("¿En qué momento del día sientes menos energía?", e.get("ev_menos_energia","")),
        ("¿Practicas actividad física al menos 3 veces/semana?", e.get("ev_actividad","")),
        ("¿Has intentado algo antes para verte/estar mejor? (Gym, Dieta, App, Otros)", e.get("ev_intentos","")),
        ("¿Qué es lo que más se te complica? (Constancia, Alimentación, Motivación, Otros)", e.get("ev_complica","")),
        ("¿Consideras que cuidar de ti es una prioridad?", e.get("ev_prioridad_personal","")),
        ("¿Consideras valioso optimizar tu presupuesto y darle prioridad a comidas y bebidas que aporten a tu bienestar y objetivos?",
         e.get("ev_valora_optimizar","")),
    ]
    metas = [
        ("Perder Peso", bool(m.get("perder_peso"))),
        ("Tonificar / Bajar Grasa", bool(m.get("tonificar"))),
        ("Aumentar Masa Muscular", bool(m.get("masa_muscular"))),
        ("Aumentar Energía", bool(m.get("energia"))),
        ("Mejorar Rendimiento Físico", bool(m.get("rendimiento"))),
        ("Mejorar Salud", bool(m.get("salud"))),
        ("Otros", m.get("otros","")),
        ("¿Qué talla te gustaría ser?", m.get("obj_talla","")),
        ("¿Qué partes del cuerpo te gustaría mejorar?", m.get("obj_partes","")),
        ("¿Qué tienes en tu ropero que podamos usar como meta?", m.get("obj_ropero","")),
        ("¿Cómo te beneficia alcanzar tu meta?", m.get("obj_beneficio","")),
        ("¿Qué eventos tienes en los próximos 3 o 6 meses?", m.get("obj_eventos","")),
        ("Nivel de compromiso (1-10)", m.get("obj_compromiso","")),
        (f"Gasto diario en comida ({cur}.)", e.get("presu_comida","")),
        (f"Gasto diario en postres/snacks/dulces ({cur}.)", e.get("presu_cafe","")),
        (f"Gasto semanal en bebidas ({cur}.)", e.get("presu_alcohol","")),
        (f"Gasto semanal en deliveries/salidas a comer ({cur}.)", e.get("presu_deliveries","")),
    ]
    composicion = [
        ("IMC", imc_val),
        ("Requerimiento de hidratación (ml/día)", agua_ml),
        ("Requerimiento de proteína (g/día)", prote_g),
        ("Metabolismo en reposo (kcal/día)", bmr_val),
        ("Objetivo calórico (kcal/día)", objetivo_kcal),
    ]
    condiciones = [
        ("¿Estreñimiento?", bool(st.session_state.get("p3_estrenimiento"))),
        ("¿Colesterol Alto?", bool(st.session_state.get("p3_colesterol_alto"))),
        ("¿Baja Energía?", bool(st.session_state.get("p3_baja_energia"))),
        ("¿Dolor Muscular?", bool(st.session_state.get("p3_dolor_muscular"))),
        ("¿Gastritis?", bool(st.session_state.get("p3_gastritis"))),
        ("¿Hemorroides?", bool(st.session_state.get("p3_hemorroides"))),
        ("¿Hipertensión?", bool(st.session_state.get("p3_hipertension"))),
        ("¿Dolor Articular?", bool(st.session_state.get("p3_dolor_articular"))),
        ("¿Ansiedad por comer?", bool(st.session_state.get("p3_ansiedad_por_comer"))),
        ("¿Jaquecas / Migrañas?", bool(st.session_state.get("p3_jaquecas_migranas"))),
        ("Diabetes (antecedentes familiares)", bool(st.session_state.get("p3_diabetes_antecedentes_familiares"))),
    ]
    seleccion = []
    if combo:
        seleccion = [
            ("Programa elegido", combo.get("titulo","")),
            ("Items", " + ".join(combo.get("items",[]))),
            ("Precio regular", combo.get("precio_regular","")),
            ("Descuento (%)", combo.get("descuento_pct","")),
            ("Precio final", combo.get("precio_final","")),
            ("Moneda", st.session_state.get("currency_symbol","S/")),
        ]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame(perfil, columns=["Pregunta","Respuesta"]).to_excel(writer, index=False, sheet_name="Perfil")
        pd.DataFrame(estilo, columns=["Pregunta","Respuesta"]).to_excel(writer, index=False, sheet_name="Estilo de Vida")
        pd.DataFrame(metas, columns=["Pregunta","Respuesta"]).to_excel(writer, index=False, sheet_name="Metas")
        pd.DataFrame(composicion, columns=["Indicador","Valor"]).to_excel(writer, index=False, sheet_name="Composición")
        pd.DataFrame(condiciones, columns=["Condición","Sí/No"]).to_excel(writer, index=False, sheet_name="Condiciones")
        if refs:
            pd.DataFrame(refs).to_excel(writer, index=False, sheet_name="Referidos")
        if seleccion:
            pd.DataFrame(seleccion, columns=["Detalle","Valor"]).to_excel(writer, index=False, sheet_name="Selección")
    buf.seek(0)
    return buf.getvalue()

# -------------------------------------------------------------
# STEP 6 - Plan Personalizado
# -------------------------------------------------------------
def pantalla6():
    st.header("6) Plan Personalizado")

    st.write(
        "Para asegurar los resultados que te has propuesto nos apoyamos en la nutrición celular del Batido de Herbalife. "
        "El cual te permite cubrir deficiencias nutricionales de nuestro día a día de manera rica, rápida y práctica."
    )

    hay = any(st.session_state.get(k, False) for k in P3_FLAGS)
    if hay:
        st.write(
            "Adicionalmente, según lo que conversamos te voy a recomendar algunos productos que pueden ayudarte "
            "a cubrir de manera específica las necesidades que me compartiste."
        )
        if st.session_state.get("p3_estrenimiento", False):
            st.write("• Para ayudarte con el estreñimiento y tengas una salud digestiva adecuada está la **fibra con sabor a manzana** para que todo te salga bien.")
        if st.session_state.get("p3_colesterol_alto", False):
            st.write("• Para mejorar tus niveles de colesterol nos apoyamos del **Herbalifeline**, unas cápsulas de concentrado de **omega 3** con sabor a menta y tomillo. Riquísimas.")
        if st.session_state.get("p3_baja_energia", False):
            nrg_name = "LiftOff" if st.session_state.get("country_code") == "CA" else ("High Protein Iced Coffee" if st.session_state.get("country_code") in ("ES-PEN","ES-CAN","IT") else "NRG")
            st.write(f"• Con el **té concentrado de hierbas** y su efecto termogénico puedes disparar tus niveles de energía y de paso quemar unas calorías extra al día. Si lo combinas con el **{nrg_name}** vas a estar totalmente lúcida y enérgica en cuerpo y mente.")
        if st.session_state.get("p3_dolor_muscular", False):
            st.write("• Para el dolor muscular se recomienda una buena ingesta de **proteína**, por lo cual el **PDM** resulta ideal al sumar de 9 a 18 g adicionales según tus requerimientos.")
        if st.session_state.get("p3_gastritis", False):
            st.write("• Para la **gastritis**, el **reflujo** y similares, el **aloe** es el indicado. Desinflama, cicatriza y alivia todo el tracto digestivo y mejora la absorción de nutrientes.")
        if st.session_state.get("p3_hemorroides", False):
            st.write("• Para la gastritis, el reflujo, **hemorroides** y similares, el **aloe** es el indicado. Desinflama, cicatriza y alivia todo el tracto digestivo y mejora la absorción de nutrientes.")
        if st.session_state.get("p3_hipertension", False):
            st.write("• Para ayudarte con la **hipertensión** te recomiendo la **Fibra Activa**, bebida alta en fibra que contribuye al control del perfil lipídico.")
        if st.session_state.get("p3_dolor_articular", False):
            if st.session_state.get("country_code") in ("CL", "US"):
                st.write("• Para el **dolor articular** está el **Collagen Drink**, ideal para mantener el cartilago sano.")
            elif st.session_state.get("country_code") in ("ES-PEN","ES-CAN"):
                st.write("• Para el **dolor articular** está el **Collagen Booster**, ideal para mantener el cartilago sano.")
            elif st.session_state.get("country_code") == "IT":
                st.write("• Para el **dolor articular** está el **Herbalifeline**, ideal para mantener el cartílago sano.")
            elif st.session_state.get("country_code") == "CA":
                st.write("• Para el **dolor articular** está el **Collagen Beauty Drink**, ideal para mantener el cartílago sano.")
            elif st.session_state.get("country_code") == "MX":
                st.write("• Para el **dolor articular** está el **Collagen Beauty Drink**, ideal para mantener el cartílago sano.")
            else:
                st.write("• Para el **dolor articular** está el **Golden Beverage**, una bebida de **cúrcuma** ideal para desinflamar las articulaciones.")
        if st.session_state.get("p3_ansiedad_por_comer", False):
            bev_name = "PPP" if st.session_state.get("country_code") in ("ES-PEN","ES-CAN","IT") else "Beverage"
            st.write(f"• La **ansiedad por comer** es síntoma de un déficit en la ingesta de proteína diaria. El **PDM** y el **{bev_name}** son ideales para aportar de 15 a 18 g adicionales al día y generar sensación de saciedad y control de antojos.")
        if st.session_state.get("p3_jaquecas_migranas", False):
            nrg_name = "LiftOff" if st.session_state.get("country_code") == "CA" else ("High Protein Iced Coffee" if st.session_state.get("country_code") in ("ES-PEN","ES-CAN","IT") else "NRG")
            st.write(f"• Para ayudarte a aliviar las **jaquecas/migranas**, el **{nrg_name}** contiene la dosis ideal de cafeína natural, además de brindarte lucidez mental.")
        if st.session_state.get("p3_diabetes_antecedentes_familiares", False):
            st.write("• Para ayudar con la **diabetes** recomendamos la **Fibra Activa**, bebida **alta en fibra** que permite reducir el índice glucémico de nuestra alimentación.")
        st.write("")

    st.divider()
    st.subheader("Servicio")
    st.write(
        "**Los primeros 10 días son clave** y estaremos contigo de cerca para construir resultados y hábitos sostenibles. "
        "Tendrás **coaching continuo, seguimiento personalizado** y revisaremos tu **diario de comidas** para que tomes conciencia de cómo tu alimentación impacta en cómo te sientes."
    )
    st.write(
        "Sabemos que en los primeros dias es cuando los hábitos antiguos presentan mayor resistencia. Por eso "
        "**el acompañamiento diario es fundamental para sostener el enfoque, aclarar dudas y ajustar lo que sea necesario en tiempo real.** "
    )
    st.write(
        "Contarás con **herramientas clave**: tus requerimientos diarios de proteína e hidratación, un **tracker de alimentación** que calcula tu progreso, y **recomendaciones de alimentos** alineadas a tus objetivos."
    )
    st.write(
        "Además tendrás: acceso a **grupos de soporte y compromiso** con motivación y aprendizajes, y a nuestra **plataforma de entrenamientos** para activarte desde donde estés."        
    )
    st.write(
        "Y por las próximas 48 horas, todos los programas tienen 5% a 10% de descuento según los productos que elijas. Te muestro las opciones más indicadas, y dime: "
        "**¿Con qué programa te permites empezar?**"
    )

    _init_promo_deadline()
    _render_countdown()
    mostrar_opciones_pantalla6()

    # Sección "Personaliza tu programa" (corregida)
    _render_personaliza_programa()

    st.markdown("### 📥 Descargar Evaluación")
    excel_bytes = _excel_bytes()
    file_country = st.session_state.get("country_code","PE")
    st.download_button(
        label="Descargar información",
        data=excel_bytes,
        file_name=f"Evaluacion_{file_country}_{st.session_state.get('datos',{}).get('nombre','usuario')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    bton_nav()

# -------------------------------------------------------------
# Side Nav
# -------------------------------------------------------------
def sidebar_nav():
    with st.sidebar:
        st.title("APP EVALUACIONES")
        st.caption(f"País: {st.session_state.get('country_name','Perú')}  ·  Moneda: {st.session_state.get('currency_symbol','S/')}")
        for i, titulo in [
            (1, "Perfil de Bienestar"),
            (2, "Composición Corporal"),
            (3, "Estilo de Vida"),
            (4, "Valoración"),
            (5, "Quiénes somos"),
            (6, "Plan Personalizado"),
        ]:
            if st.button(f"{i}. {titulo}", use_container_width=True):
                go(to=i)

        st.markdown("---")
        st.markdown("**Selección actual (debug):**")
        st.write(st.session_state.get("combo_elegido"))

# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
def main():
    init_state()
    inject_theme()  # <<< aplica la nueva paleta/estilos inspirada en la plantilla Wix
    sidebar_nav()
    s = st.session_state.step
    if s == 1: pantalla1()
    elif s == 2: pantalla2()
    elif s == 3: pantalla3()
    elif s == 4: pantalla4()
    elif s == 5: pantalla5()
    elif s == 6: pantalla6()

if __name__ == "__main__":
    main()
