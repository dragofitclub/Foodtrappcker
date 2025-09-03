# app_diario_comidas_v10_reset_midnight.py
# -*- coding: utf-8 -*-

from datetime import datetime, date
from typing import List, Dict
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------- Config ----------
st.set_page_config(page_title="Diario de Comidas (Reset 00:00)", layout="wide")
HORA_FMT = "%H:%M"

# Claves en localStorage
LS_DATA_KEY = "diario_comidas_v9"       # perfil + logs
LS_META_KEY = "diario_comidas_v9_meta"  # {"last_reset":"YYYY-MM-DD"}

# ---------- CSS (responsive/compacto) ----------
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 1.25rem;}
.fullwidth .stButton>button {width: 100%;}
input, textarea, select {font-size: 0.95rem;}
[data-baseweb="select"] {font-size: 0.95rem;}
div[data-testid="stHorizontalBlock"] {overflow-x: hidden;}
[role="progressbar"] div {font-size: 0.9rem;}
@media (max-width: 640px) {
  .block-container {padding-left: 0.8rem; padding-right: 0.8rem;}
  h1, h2, h3 {font-size: 1.05rem;}
  .stTabs [role="tablist"] {gap: .25rem;}
  .stTabs [role="tab"] {padding: .3rem .55rem;}
  .stDataFrame {font-size: 0.9rem;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# BASE INCRUSTADA DESDE EXCEL (hoja BibliotecaComida)
# No depende de archivos externos.
# Campos: nombre | porcion_desc | kcal | proteina_g | hidr_ml (0 por defecto)
# =========================
BASE_INTERNA: List[Dict] = [
  {
    "nombre": "Pechuga de pollo (cruda, sin piel)",
    "porcion_desc": "100g",
    "kcal": 120.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pavo (pechuga cruda, sin piel)",
    "porcion_desc": "100g",
    "kcal": 110.0,
    "proteina_g": 21.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chuleta de cerdo magra (cruda)",
    "porcion_desc": "100g",
    "kcal": 143.0,
    "proteina_g": 21.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Salmón (crudo)",
    "porcion_desc": "100g",
    "kcal": 142.0,
    "proteina_g": 20.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Atún fresco (crudo)",
    "porcion_desc": "100g",
    "kcal": 144.0,
    "proteina_g": 23.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Merluza (cruda, pescado blanco)",
    "porcion_desc": "100g",
    "kcal": 85.0,
    "proteina_g": 18.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Bacalao (crudo, pescado blanco)",
    "porcion_desc": "100g",
    "kcal": 82.0,
    "proteina_g": 18.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tilapia (cruda)",
    "porcion_desc": "100g",
    "kcal": 96.0,
    "proteina_g": 20.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Camarones (crudos)",
    "porcion_desc": "100g",
    "kcal": 99.0,
    "proteina_g": 24.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Huevo entero",
    "porcion_desc": "1 unidad",
    "kcal": 70.0,
    "proteina_g": 6.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Huevo griego descremado",
    "porcion_desc": "100g",
    "kcal": 59.0,
    "proteina_g": 10.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Requesón (cottage 2%)",
    "porcion_desc": "100g",
    "kcal": 82.0,
    "proteina_g": 11.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Legumbres (cocidas, secas, crudas)",
    "porcion_desc": "100g",
    "kcal": 116.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Edamame (vaina verde, crudo)",
    "porcion_desc": "100g",
    "kcal": 122.0,
    "proteina_g": 11.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tofu firme",
    "porcion_desc": "100g",
    "kcal": 76.0,
    "proteina_g": 8.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Batido Nutricional",
    "porcion_desc": "1 scoop",
    "kcal": 90.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "PDM",
    "porcion_desc": "1 scoop",
    "kcal": 55.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Nutrib Boost",
    "porcion_desc": "1 scoop",
    "kcal": 45.0,
    "proteina_g": 4.5,
    "hidr_ml": 0
  },
  {
    "nombre": "H24 Rebuild Strength",
    "porcion_desc": "1 scoop",
    "kcal": 190.0,
    "proteina_g": 24.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Crocante de Proteina",
    "porcion_desc": "1 barra",
    "kcal": 37.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Bebida Pro H24",
    "porcion_desc": "1 sobre",
    "kcal": 35.0,
    "proteina_g": 17.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Beverage Mix",
    "porcion_desc": "1 scoop",
    "kcal": 37.0,
    "proteina_g": 15.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Batido Nutricional en Polvo",
    "porcion_desc": "1 scoop",
    "kcal": 90.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Lentejas (cocidas)",
    "porcion_desc": "100g",
    "kcal": 116.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Garbanzos (cocidos)",
    "porcion_desc": "100g",
    "kcal": 164.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Frijoles (cocidos)",
    "porcion_desc": "100g",
    "kcal": 127.0,
    "proteina_g": 8.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arvejas (cocidas)",
    "porcion_desc": "100g",
    "kcal": 84.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Espinaca",
    "porcion_desc": "100g",
    "kcal": 23.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Brócoli",
    "porcion_desc": "100g",
    "kcal": 34.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Zanahoria",
    "porcion_desc": "100g",
    "kcal": 41.0,
    "proteina_g": 1.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pepino",
    "porcion_desc": "100g",
    "kcal": 16.0,
    "proteina_g": 0.7,
    "hidr_ml": 0
  },
  {
    "nombre": "Cebolla",
    "porcion_desc": "100g",
    "kcal": 40.0,
    "proteina_g": 1.1,
    "hidr_ml": 0
  },
  {
    "nombre": "Pimiento",
    "porcion_desc": "100g",
    "kcal": 31.0,
    "proteina_g": 1.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tomate",
    "porcion_desc": "100g",
    "kcal": 18.0,
    "proteina_g": 0.9,
    "hidr_ml": 0
  },
  {
    "nombre": "Plátano",
    "porcion_desc": "1 unidad",
    "kcal": 105.0,
    "proteina_g": 1.3,
    "hidr_ml": 0
  },
  {
    "nombre": "Manzana",
    "porcion_desc": "1 unidad",
    "kcal": 95.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Pera",
    "porcion_desc": "1 unidad",
    "kcal": 101.0,
    "proteina_g": 0.6,
    "hidr_ml": 0
  },
  {
    "nombre": "Naranja",
    "porcion_desc": "1 unidad",
    "kcal": 62.0,
    "proteina_g": 1.2,
    "hidr_ml": 0
  },
  {
    "nombre": "Mandarina",
    "porcion_desc": "1 unidad",
    "kcal": 47.0,
    "proteina_g": 0.7,
    "hidr_ml": 0
  },
  {
    "nombre": "Piña",
    "porcion_desc": "1 taza (165g)",
    "kcal": 82.0,
    "proteina_g": 0.9,
    "hidr_ml": 0
  },
  {
    "nombre": "Papaya",
    "porcion_desc": "1 taza (145g)",
    "kcal": 62.0,
    "proteina_g": 0.7,
    "hidr_ml": 0
  },
  {
    "nombre": "Mango",
    "porcion_desc": "1 taza (165g)",
    "kcal": 99.0,
    "proteina_g": 1.4,
    "hidr_ml": 0
  },
  {
    "nombre": "Uvas",
    "porcion_desc": "1 puñado (80g)",
    "kcal": 55.0,
    "proteina_g": 0.6,
    "hidr_ml": 0
  },
  {
    "nombre": "Fresas",
    "porcion_desc": "1 puñado (100g)",
    "kcal": 33.0,
    "proteina_g": 0.7,
    "hidr_ml": 0
  },
  {
    "nombre": "Kiwi",
    "porcion_desc": "1 unidad",
    "kcal": 42.0,
    "proteina_g": 0.8,
    "hidr_ml": 0
  },
  {
    "nombre": "Almendras",
    "porcion_desc": "1 puñado (28g)",
    "kcal": 170.0,
    "proteina_g": 6.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Maní (cacahuate)",
    "porcion_desc": "1 puñado (28g)",
    "kcal": 165.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Nueces",
    "porcion_desc": "1 puñado (28g)",
    "kcal": 185.0,
    "proteina_g": 4.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arroz Blanco (Cocido)",
    "porcion_desc": "1 taza (150g)",
    "kcal": 200.0,
    "proteina_g": 4.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arroz Integral (Cocido)",
    "porcion_desc": "1 taza (150g)",
    "kcal": 215.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pasta Blanca (Cocida)",
    "porcion_desc": "1 taza (150g)",
    "kcal": 220.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Papa (Cocida)",
    "porcion_desc": "150g",
    "kcal": 130.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Camote (Cocido)",
    "porcion_desc": "150g",
    "kcal": 135.0,
    "proteina_g": 2.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Quinua (Cocida)",
    "porcion_desc": "1 taza (185g)",
    "kcal": 222.0,
    "proteina_g": 8.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Avena (Cocida)",
    "porcion_desc": "1 taza (234g)",
    "kcal": 154.0,
    "proteina_g": 6.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pasta Integral (Cocida)",
    "porcion_desc": "1 taza (150g)",
    "kcal": 210.0,
    "proteina_g": 8.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Aceitunas",
    "porcion_desc": "100g",
    "kcal": 115.0,
    "proteina_g": 0.8,
    "hidr_ml": 0
  },
  {
    "nombre": "Herbal Aloe Concentrado",
    "porcion_desc": "3 tapas",
    "kcal": 1.8,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "N-R-G",
    "porcion_desc": "1/2 cucharadita",
    "kcal": 3.4,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Té Concentrado de Hierbas",
    "porcion_desc": "1/2 cucharadita",
    "kcal": 6.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "CR7 Drive",
    "porcion_desc": "1 scoop",
    "kcal": 50.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "RLX",
    "porcion_desc": "1 sobre",
    "kcal": 5.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Collagen Beauty Drink",
    "porcion_desc": "1 scoop",
    "kcal": 25.0,
    "proteina_g": 2.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Niteworks",
    "porcion_desc": "1 scoop",
    "kcal": 25.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Immune Essentials",
    "porcion_desc": "1 scoop",
    "kcal": 25.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Complex Multivitamínico",
    "porcion_desc": "1 cápsula",
    "kcal": 5.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Her Calic",
    "porcion_desc": "1 cápsula",
    "kcal": 5.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Omeg 3",
    "porcion_desc": "1 cápsula",
    "kcal": 10.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Xtra Cal",
    "porcion_desc": "1 cápsula",
    "kcal": 10.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Queso Cheddar",
    "porcion_desc": "10 laminas (20g)",
    "kcal": 270.0,
    "proteina_g": 18.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Queso Edam",
    "porcion_desc": "100g",
    "kcal": 350.0,
    "proteina_g": 25.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Queso Mozzarella",
    "porcion_desc": "100g",
    "kcal": 280.0,
    "proteina_g": 28.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Yogurt Griego",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 136.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Yogurt Griego Light",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 125.0,
    "proteina_g": 15.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Yogurt Natural",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 118.0,
    "proteina_g": 6.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Leche evaporada (diluida)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 155.0,
    "proteina_g": 8.8,
    "hidr_ml": 0
  },
  {
    "nombre": "Leche de vaca (deslactosada)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 115.0,
    "proteina_g": 8.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Leche de soya (sin azúcar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 95.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Leche de almendras (sin azúcar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 35.0,
    "proteina_g": 1.2,
    "hidr_ml": 0
  },
  {
    "nombre": "Tomate (unidad)",
    "porcion_desc": "1 unidad",
    "kcal": 18.0,
    "proteina_g": 0.9,
    "hidr_ml": 0
  },
  {
    "nombre": "Manzana (unidad)",
    "porcion_desc": "1 unidad",
    "kcal": 95.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Pera (unidad)",
    "porcion_desc": "1 unidad",
    "kcal": 101.0,
    "proteina_g": 0.6,
    "hidr_ml": 0
  },
  {
    "nombre": "Uva",
    "porcion_desc": "1 puñado (80g)",
    "kcal": 55.0,
    "proteina_g": 0.6,
    "hidr_ml": 0
  },
  {
    "nombre": "Plátano (unidad)",
    "porcion_desc": "1 unidad",
    "kcal": 105.0,
    "proteina_g": 1.3,
    "hidr_ml": 0
  },
  {
    "nombre": "Pan de molde blanco",
    "porcion_desc": "1 tajada",
    "kcal": 80.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pan de molde integral",
    "porcion_desc": "1 tajada",
    "kcal": 80.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pan francés",
    "porcion_desc": "1 unidad",
    "kcal": 160.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pan ciabatta",
    "porcion_desc": "1 unidad",
    "kcal": 260.0,
    "proteina_g": 9.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arándanos",
    "porcion_desc": "1 puñado (70g)",
    "kcal": 40.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Frambuesas",
    "porcion_desc": "1 puñado (70g)",
    "kcal": 32.0,
    "proteina_g": 0.7,
    "hidr_ml": 0
  },
  {
    "nombre": "Zarzamoras",
    "porcion_desc": "1 puñado (70g)",
    "kcal": 43.0,
    "proteina_g": 1.4,
    "hidr_ml": 0
  },
  {
    "nombre": "Lechuga",
    "porcion_desc": "1 taza (50g)",
    "kcal": 8.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Yogurt Danlac Griego Natural",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 136.0,
    "proteina_g": 7.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Yogurt Danlac Descremado Natural",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 126.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arroz Chaufa (Carta)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 520.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chaufa de Pollo (Carta)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 520.0,
    "proteina_g": 32.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chaufa Especial (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 600.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Arroz Aeroporto (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 600.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tallarín Saltado de Pollo (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 540.0,
    "proteina_g": 24.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tallarín Taypa (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 620.0,
    "proteina_g": 26.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pollo con Kion (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 410.0,
    "proteina_g": 28.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chanchito con tamarindo (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 600.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pollo Enrollado (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 450.0,
    "proteina_g": 36.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Lomo en Ostión (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 430.0,
    "proteina_g": 32.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Sopa Wantan (Menu)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 300.0,
    "proteina_g": 16.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Ceviche (Composición)",
    "porcion_desc": "1 plato (250g)",
    "kcal": 400.0,
    "proteina_g": 36.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chifa Casa",
    "porcion_desc": "1 unidad",
    "kcal": 450.0,
    "proteina_g": 28.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Whopper BK",
    "porcion_desc": "1 unidad",
    "kcal": 556.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Whopper Cheese BK",
    "porcion_desc": "1 unidad",
    "kcal": 594.0,
    "proteina_g": 26.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Whopper Doble BK",
    "porcion_desc": "1 unidad",
    "kcal": 899.0,
    "proteina_g": 53.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Whopper Doble Cheese BK",
    "porcion_desc": "1 unidad",
    "kcal": 937.0,
    "proteina_g": 57.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chicken Burger BK",
    "porcion_desc": "1 unidad",
    "kcal": 453.0,
    "proteina_g": 15.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Stacker BK",
    "porcion_desc": "1 unidad",
    "kcal": 462.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Papas Fritas BK",
    "porcion_desc": "1 unidad",
    "kcal": 328.0,
    "proteina_g": 4.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Papas Fritas Grandes BK",
    "porcion_desc": "1 unidad",
    "kcal": 430.0,
    "proteina_g": 5.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Gaseosa 21oz",
    "porcion_desc": "1 unidad",
    "kcal": 242.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Gaseosa 16oz",
    "porcion_desc": "1 unidad",
    "kcal": 184.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Gaseosa 20oz",
    "porcion_desc": "1 unidad",
    "kcal": 230.0,
    "proteina_g": 0.0,
    "hidr_ml": 0
  },
  {
    "nombre": "MC Donalds Classic",
    "porcion_desc": "1 unidad",
    "kcal": 390.0,
    "proteina_g": 12.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Cheese",
    "porcion_desc": "1 unidad",
    "kcal": 320.0,
    "proteina_g": 13.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Doble Cheese",
    "porcion_desc": "1 unidad",
    "kcal": 450.0,
    "proteina_g": 23.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Doble con Queso",
    "porcion_desc": "1 unidad",
    "kcal": 410.0,
    "proteina_g": 22.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Chicken",
    "porcion_desc": "1 unidad",
    "kcal": 470.0,
    "proteina_g": 15.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Nuggets 10",
    "porcion_desc": "1 unidad",
    "kcal": 530.0,
    "proteina_g": 26.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Mc Donalds Papas",
    "porcion_desc": "1 unidad",
    "kcal": 340.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pollo a la brasa (1/4 sin guarnición)",
    "porcion_desc": "200g",
    "kcal": 350.0,
    "proteina_g": 58.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Pollo a la brasa 1/4 (completo)",
    "porcion_desc": "1 unidad",
    "kcal": 1500.0,
    "proteina_g": 120.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Chicharrones Caseros",
    "porcion_desc": "1 unidad",
    "kcal": 680.0,
    "proteina_g": 45.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Tocino",
    "porcion_desc": "1 unidad",
    "kcal": 45.0,
    "proteina_g": 3.0,
    "hidr_ml": 0
  },
  {
    "nombre": "Limonada (con azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 120.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Limonada (sin azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 30.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Chicha (sin azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 35.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Chicha (Con azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 100.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Maracuya (sin azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 35.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Maracuya (con azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 110.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Emoliente (sin azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 15.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  },
  {
    "nombre": "Emoliente (con azucar)",
    "porcion_desc": "1 vaso (250ml)",
    "kcal": 15.0,
    "proteina_g": 0.5,
    "hidr_ml": 0
  }
]

alimentos_df = pd.DataFrame(BASE_INTERNA).sort_values("nombre").reset_index(drop=True)

# =========================
# Cálculos de metas
# =========================
OBJETIVOS_FUERZA = {"Aumentar masa muscular", "Mejorar rendimiento físico", "Mejorar rendimiento fisico"}

def meta_proteina(peso_kg: float, genero: str, objetivos: List[str]) -> float:
    especial = bool(OBJETIVOS_FUERZA.intersection(set(map(str.strip, objetivos))))
    if (genero or "").lower().startswith("h"):
        factor = 2.0 if especial else 1.6
    else:
        factor = 1.8 if especial else 1.4
    return round(peso_kg * factor, 1)

def meta_calorias(peso_kg: float, altura_cm: float, edad: int, genero: str, objetivos: List[str]) -> int:
    if (genero or "").lower().startswith("h"):
        bmr = (10*peso_kg) + (6.25*altura_cm) - (5*edad) + 5
        ajuste = 250 if OBJETIVOS_FUERZA.intersection(objetivos) else -250
    else:
        bmr = (10*peso_kg) + (6.25*altura_cm) - (5*edad) - 161
        ajuste = 250 if OBJETIVOS_FUERZA.intersection(objetivos) else -250
    req = int(round(bmr + ajuste))
    return max(req, 1200) if ajuste < 0 else req

def meta_agua_ml(peso_kg: float) -> int:
    return int(round((peso_kg/7.0)*250))

def totales_del_dia(rows: List[Dict]):
    kcal = sum(r["kcal_tot"] for r in rows if r["tipo"] == "Comida")
    prot = sum(r["prot_tot"] for r in rows if r["tipo"] == "Comida")
    agua = sum(r.get("hidr_tot_ml", 0) for r in rows)
    return kcal, prot, agua

def numero_color(valor: float, meta: float, tipo: str):
    color = "green" if (valor <= meta if tipo == "kcal" else valor >= meta) else "red"
    txt = f"{valor:,.1f}" if isinstance(valor, float) and not float(valor).is_integer() else f"{int(valor):,}"
    st.markdown(f"<span style='color:{color}; font-weight:700'>{txt}</span>", unsafe_allow_html=True)

def fila_resumen(label: str, consumido: float, meta: float, tipo: str):
    c1, c2, c3 = st.columns([1,1,1])
    with c1: st.markdown(f"**{label}**")
    with c2: numero_color(consumido, meta, tipo)
    with c3: st.markdown(f"de **{int(meta) if tipo=='kcal' else round(meta,1)}**")

# =========================
# Estado base
# =========================
if "logs" not in st.session_state:
    st.session_state.logs = {}            # {"YYYY-MM-DD": [registros]}
if "perfil" not in st.session_state:
    st.session_state.perfil = {}          # nombre, genero, edad, peso, altura, objetivos
if "initialized_from_ls" not in st.session_state:
    st.session_state.initialized_from_ls = False
if "last_reset" not in st.session_state:
    st.session_state.last_reset = None    # "YYYY-MM-DD" de la última limpieza

def _key_fecha(d: date) -> str: return d.isoformat()
def get_logs_del_dia(d: date): return st.session_state.logs.get(_key_fecha(d), [])
def set_logs_del_dia(d: date, rows): st.session_state.logs[_key_fecha(d)] = rows

# =========================
# Helpers JS para LocalStorage y fecha local del dispositivo
# =========================
def ls_get(key: str) -> str:
    return components.html(f"""
    <script>
      const v = window.localStorage.getItem("{key}") ?? "";
      Streamlit.setComponentValue(v);
    </script>
    """, height=0)

def ls_set(key: str, value: str):
    components.html(f"""
    <script>
      try {{ window.localStorage.setItem("{key}", {json.dumps(value)}); }}
      catch (e) {{ console.warn("localStorage set failed", e); }}
    </script>
    """, height=0)

def get_client_ymd() -> str:
    """Devuelve 'YYYY-MM-DD' según la hora LOCAL del dispositivo."""
    return components.html("""
    <script>
      const d = new Date();
      const y = d.getFullYear();
      const m = String(d.getMonth()+1).padStart(2,'0');
      const da = String(d.getDate()).padStart(2,'0');
      Streamlit.setComponentValue(`${y}-${m}-${da}`);
    </script>
    """, height=0)

# =========================
# Cargar desde localStorage + auto-reset por día
# =========================
if not st.session_state.initialized_from_ls:
    # 1) Carga data (perfil + logs)
    raw = ls_get(LS_DATA_KEY)
    try:
        if isinstance(raw, str) and raw.strip():
            payload = json.loads(raw)
            if isinstance(payload.get("perfil"), dict):
                st.session_state.perfil = payload["perfil"]
            if isinstance(payload.get("logs"), dict):
                st.session_state.logs = payload["logs"]
    except Exception:
        pass

    # 2) Carga meta (last_reset)
    raw_meta = ls_get(LS_META_KEY)
    meta_obj = {}
    try:
        if isinstance(raw_meta, str) and raw_meta.strip():
            meta_obj = json.loads(raw_meta)
    except Exception:
        meta_obj = {}

    # 3) Fecha local del dispositivo
    client_ymd = get_client_ymd()
    if not isinstance(client_ymd, str) or not client_ymd.strip():
        client_ymd = date.today().isoformat()  # fallback por si algo falla

    last_reset = (meta_obj.get("last_reset") if isinstance(meta_obj, dict) else None)

    # 4) Si cambió el día → limpiar SOLO logs
    if last_reset != client_ymd:
        st.session_state.logs = {}  # limpiar registros diarios
        st.session_state.last_reset = client_ymd
        # Persistir meta actualizada
        try:
            ls_set(LS_META_KEY, json.dumps({"last_reset": client_ymd}))
        except Exception:
            pass
    else:
        st.session_state.last_reset = last_reset

    st.session_state.initialized_from_ls = True

# =========================
# Header + modo móvil con query param estable
# =========================
st.title("Diario de Comidas")

qp = st.query_params
arrancar_movil = str(qp.get("movil", "0")).lower() in ("1", "true", "yes", "y")

if "modo_movil" not in st.session_state:
    st.session_state.modo_movil = arrancar_movil

modo_movil = st.toggle("📱 Modo compacto (móvil)", value=st.session_state.modo_movil,
                       help="Optimiza controles para pantallas chicas")
st.session_state.modo_movil = modo_movil

# sincroniza URL
if modo_movil:
    st.query_params["movil"] = "1"
else:
    if "movil" in st.query_params:
        del st.query_params["movil"]

container_btn_class = "fullwidth" if modo_movil else ""

# =========================
# Inputs del usuario (usa perfil guardado si existe)
# =========================
def ui_datos():
    pf = st.session_state.perfil or {}
    nombre = st.text_input("Nombre", pf.get("nombre", ""))
    genero = st.selectbox("Género", ["Hombre", "Mujer"], index=(0 if pf.get("genero","Hombre")=="Hombre" else 1))
    edad = st.number_input("Edad (años)", min_value=10, max_value=100, value=int(pf.get("edad", 30)), step=1)
    peso = st.number_input("Peso (kg)", min_value=20.0, max_value=300.0,
                           value=float(pf.get("peso", 70.0)), step=0.5, format="%.1f")
    altura = st.number_input("Altura (cm)", min_value=120.0, max_value=230.0,
                             value=float(pf.get("altura", 170.0)), step=0.5, format="%.1f")
    objetivos = st.multiselect("Objetivo(s)",
                               ["Bajar grasa","Mantener","Aumentar masa muscular","Mejorar rendimiento físico"],
                               default=pf.get("objetivos", []))
    st.caption("Si marcas *Aumentar masa muscular* o *Mejorar rendimiento físico*, las metas se ajustan.")
    st.session_state.perfil = {
        "nombre": nombre, "genero": genero, "edad": int(edad),
        "peso": float(peso), "altura": float(altura), "objetivos": objetivos
    }
    return nombre, genero, edad, peso, altura, objetivos

if modo_movil:
    with st.expander("🧍 Datos de la persona", expanded=True):
        nombre, genero, edad, peso, altura, objetivos = ui_datos()
else:
    with st.sidebar:
        st.header("🧍 Datos de la persona")
        nombre, genero, edad, peso, altura, objetivos = ui_datos()

# =========================
# Fecha + metas
# =========================
cfecha, _ = st.columns([1,3])
with cfecha:
    fecha_sel = st.date_input("📅 Fecha del diario", value=date.today())

meta_prot = meta_proteina(peso, genero, objetivos)
meta_cal  = meta_calorias(peso, altura, edad, genero, objetivos)
meta_h2o  = meta_agua_ml(peso)

# =========================
# Progreso
# =========================
def totales_del_dia(rows: List[Dict]):
    kcal = sum(r["kcal_tot"] for r in rows if r["tipo"] == "Comida")
    prot = sum(r["prot_tot"] for r in rows if r["tipo"] == "Comida")
    agua = sum(r.get("hidr_tot_ml", 0) for r in rows)
    return kcal, prot, agua

logs_hoy = get_logs_del_dia(fecha_sel)
kcal_tot, prot_tot, agua_tot_ml = totales_del_dia(logs_hoy)

st.subheader("Progreso del día")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**Calorías**")
    st.progress(min(kcal_tot/max(meta_cal,1), 1.0), text=f"{kcal_tot} / {meta_cal} kcal")
with p2:
    st.markdown("**Proteína**")
    st.progress(min(prot_tot/max(meta_prot,1e-9), 1.0), text=f"{prot_tot:.1f} / {meta_prot:.1f} g")
with p3:
    st.markdown("**Hidratación**")
    st.progress(min(agua_tot_ml/max(meta_h2o,1), 1.0), text=f"{agua_tot_ml} / {meta_h2o} ml")

st.divider()

# =========================
# Tabs
# =========================
tab_agregar, tab_resumen, tab_base = st.tabs(["➕ Agregar registro", "📊 Resumen del día", "🍽️ Base de alimentos"])

with tab_agregar:
    tipo_reg = st.radio("Tipo de registro", ["Comida", "Hidratación"], horizontal=not modo_movil)

    if tipo_reg == "Comida":
        opciones = alimentos_df.copy()
        opciones["etiqueta"] = opciones.apply(
            lambda r: f'{r["nombre"]} · {r["porcion_desc"]} ({int(r["kcal"])} kcal, {r["proteina_g"]:.1f} g prot)', axis=1
        )
        seleccion = st.selectbox(
            "Buscar y elegir alimento (escribe para filtrar)",
            options=opciones.index.tolist(),
            format_func=lambda i: opciones.loc[i, "etiqueta"],
            index=None,
            placeholder="pollo, arroz, yogurt…"
        )
        porciones = st.number_input("Porciones", min_value=0.25, max_value=10.0, value=1.0, step=0.25)

        st.markdown(f'<div class="{container_btn_class}">', unsafe_allow_html=True)
        add = st.button("Agregar comida", type="primary", disabled=(seleccion is None), use_container_width=modo_movil)
        st.markdown('</div>', unsafe_allow_html=True)

        if add and seleccion is not None:
            row = opciones.loc[seleccion]
            nuevo = {
                "hora": datetime.now().strftime(HORA_FMT),
                "tipo": "Comida",
                "alimento": row["nombre"],
                "porcion": row["porcion_desc"],
                "porciones": porciones,
                "kcal_unit": float(row["kcal"]),
                "prot_unit": float(row["proteina_g"]),
                "hidr_unit_ml": float(row.get("hidr_ml", 0) or 0),
                "kcal_tot": float(row["kcal"]) * porciones,
                "prot_tot": float(row["proteina_g"]) * porciones,
                "hidr_tot_ml": float(row.get("hidr_ml", 0) or 0) * porciones,
            }
            rows = get_logs_del_dia(fecha_sel)
            rows.append(nuevo)
            set_logs_del_dia(fecha_sel, rows)
            st.success("Comida agregada ✅")

    else:
        ml = st.number_input("Mililitros (ml)", min_value=50, max_value=3000, value=250, step=50)
        detalle = st.text_input("Detalle (opcional)", "Agua")

        st.markdown(f'<div class="{container_btn_class}">', unsafe_allow_html=True)
        addw = st.button("Agregar hidratación", type="primary", use_container_width=modo_movil)
        st.markdown('</div>', unsafe_allow_html=True)

        if addw:
            nuevo = {
                "hora": datetime.now().strftime(HORA_FMT),
                "tipo": "Hidratación",
                "alimento": detalle,
                "porcion": f"{ml} ml",
                "porciones": 1.0,
                "kcal_unit": 0.0,
                "prot_unit": 0.0,
                "hidr_unit_ml": float(ml),
                "kcal_tot": 0.0,
                "prot_tot": 0.0,
                "hidr_tot_ml": float(ml),
            }
            rows = get_logs_del_dia(fecha_sel)
            rows.append(nuevo)
            set_logs_del_dia(fecha_sel, rows)
            st.success("Hidratación agregada 💧")

with tab_resumen:
    rows = get_logs_del_dia(fecha_sel)
    if not rows:
        st.info("Aún no hay registros en esta fecha.")
    else:
        df = pd.DataFrame(rows)
        df_view = df[["hora","tipo","alimento","porcion","porciones","kcal_tot","prot_tot","hidr_tot_ml"]].copy()
        df_view.columns = ["Hora","Tipo","Alimento","Porción","Porciones","Kcal","Proteína (g)","Hidratación (ml)"]
        st.dataframe(df_view, use_container_width=True, height=360)

        kcal_tot, prot_tot, agua_tot_ml = totales_del_dia(rows)
        st.subheader("Totales")
        c1, c2, c3 = st.columns(3)
        with c1: fila_resumen("Calorías", kcal_tot, meta_cal, "kcal")
        with c2: fila_resumen("Proteína (g)", prot_tot, meta_prot, "prot")
        with c3: fila_resumen("Hidratación (ml)", agua_tot_ml, meta_h2o, "agua")

        st.divider()
        cdel1, cdel2 = st.columns(2)
        with cdel1:
            st.markdown(f'<div class="{container_btn_class}">', unsafe_allow_html=True)
            if st.button("🗑️ Borrar último", use_container_width=modo_movil):
                rows.pop()
                set_logs_del_dia(fecha_sel, rows)
                st.warning("Se borró el último registro.")
            st.markdown('</div>', unsafe_allow_html=True)
        with cdel2:
            st.markdown(f'<div class="{container_btn_class}">', unsafe_allow_html=True)
            if st.button("🗑️ Vaciar día", use_container_width=modo_movil):
                set_logs_del_dia(fecha_sel, [])
                st.warning("Se vaciaron los registros del día.")
            st.markdown('</div>', unsafe_allow_html=True)

with tab_base:
    st.markdown("**Base de alimentos (incrustada)**")
    st.dataframe(alimentos_df, use_container_width=True, height=420)
    st.success(f"Alimentos cargados: {len(alimentos_df)}")

# =========================
# Persistencia en localStorage (guardar al final de cada ejecución)
# =========================
try:
    payload = {"perfil": st.session_state.perfil, "logs": st.session_state.logs}
    components.html(f"""
    <script>
      try {{
        window.localStorage.setItem("{LS_DATA_KEY}", {json.dumps(json.dumps(payload, ensure_ascii=False))});
        // Asegura que meta tenga last_reset actual (si ya lo definimos arriba)
        const metaRaw = window.localStorage.getItem("{LS_META_KEY}");
        let meta = metaRaw ? JSON.parse(metaRaw) : {{}};
        if (!meta.last_reset && "{st.session_state.last_reset or ''}") {{
          meta.last_reset = "{st.session_state.last_reset or ''}";
          window.localStorage.setItem("{LS_META_KEY}", JSON.stringify(meta));
        }}
      }} catch (e) {{ console.warn("localStorage set failed", e); }}
    </script>
    """, height=0)
except Exception:
    pass

st.caption("App Diario de Comidas · v10 · Persistencia local + Auto-reset diario a medianoche (hora local del dispositivo)")
