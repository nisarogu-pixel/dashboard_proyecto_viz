import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HR Attrition Dashboard | IBM",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# PALETA DE COLORES SEMÁNTICA (Teoría del color)
# Rojo = rota (alerta), Azul = se queda (estable)
# 3-5 colores base, variaciones de tono
# ─────────────────────────────────────────────
C_ATTRITION   = "#E63946"   # rojo — empleados que se van (alerta)
C_RETENTION   = "#1D6FA4"   # azul oscuro — empleados que se quedan
C_ACCENT      = "#F4A261"   # naranja — destacado neutro
C_DARK_BG     = "#0F1117"   # fondo principal
C_CARD_BG     = "#1C1F2E"   # fondo cards
C_BORDER      = "#2D3250"   # bordes sutiles
C_TEXT_MAIN   = "#EAEAEA"   # texto principal
C_TEXT_MUTED  = "#8A8FAF"   # texto secundario
C_GREEN       = "#2EC4B6"   # verde agua — indicador positivo

# ─────────────────────────────────────────────
# CSS GLOBAL — Roboto, jerarquía, espacios, sin ruido
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Roboto', sans-serif;
    background-color: {C_DARK_BG};
    color: {C_TEXT_MAIN};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {C_CARD_BG};
    border-right: 1px solid {C_BORDER};
  }}
  section[data-testid="stSidebar"] * {{
    color: {C_TEXT_MAIN} !important;
  }}

  /* Eliminar padding excesivo */
  .block-container {{ padding-top: 1.5rem; padding-bottom: 1rem; }}

  /* KPI Cards */
  .kpi-card {{
    background-color: {C_CARD_BG};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 20px 18px 16px 18px;
    text-align: center;
    height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}
  .kpi-label {{
    font-size: 12px;
    font-weight: 500;
    color: {C_TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
  }}
  .kpi-value {{
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }}
  .kpi-sub {{
    font-size: 11px;
    color: {C_TEXT_MUTED};
    margin-top: 4px;
  }}

  /* Títulos de sección */
  .section-title {{
    font-size: 14px;
    font-weight: 700;
    color: {C_TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 18px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid {C_BORDER};
  }}

  /* Header principal */
  .main-header {{
    background: linear-gradient(90deg, {C_CARD_BG} 0%, #1a1f38 100%);
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 18px;
  }}
  .main-title {{
    font-size: 26px;
    font-weight: 700;
    color: {C_TEXT_MAIN};
    margin: 0;
  }}
  .main-subtitle {{
    font-size: 13px;
    color: {C_TEXT_MUTED};
    margin: 4px 0 0 0;
  }}

  /* Insight box */
  .insight-box {{
    background-color: {C_CARD_BG};
    border-left: 3px solid {C_ATTRITION};
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
    color: {C_TEXT_MAIN};
  }}
  .insight-box.positive {{
    border-left-color: {C_GREEN};
  }}

  /* Ocultar elementos de Streamlit innecesarios */
  #MainMenu, footer {{ visibility: hidden; }}
  .stDeployButton {{ display: none; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA Y PREPARACIÓN DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
    # Variables derivadas
    df["AttritionBin"] = (df["Attrition"] == "Yes").astype(int)
    df["AgeBin"] = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 55, 65],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"]
    )
    df["SatisfaccionLabel"] = df["JobSatisfaction"].map(
        {1: "Baja (1)", 2: "Media-baja (2)", 3: "Media-alta (3)", 4: "Alta (4)"}
    )
    df["WLBLabel"] = df["WorkLifeBalance"].map(
        {1: "Malo (1)", 2: "Regular (2)", 3: "Bueno (3)", 4: "Excelente (4)"}
    )
    return df

df = load_data()


# ─────────────────────────────────────────────
# SIDEBAR — FILTROS INTERACTIVOS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 18px 0;'>
      <span style='font-size:32px;'>👥</span>
      <p style='font-size:16px; font-weight:700; margin:6px 0 2px 0;'>HR Analytics</p>
      <p style='font-size:11px; color:#8A8FAF;'>IBM Employee Attrition</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔍 Filtros")

    dept_options = ["Todos"] + sorted(df["Department"].unique().tolist())
    dept_sel = st.selectbox("Departamento", dept_options)

    gender_options = ["Todos"] + sorted(df["Gender"].unique().tolist())
    gender_sel = st.selectbox("Género", gender_options)

    overtime_options = ["Todos", "Con Overtime", "Sin Overtime"]
    overtime_sel = st.selectbox("Overtime", overtime_options)

    marital_options = ["Todos"] + sorted(df["MaritalStatus"].unique().tolist())
    marital_sel = st.selectbox("Estado Civil", marital_options)

    age_range = st.slider(
        "Rango de Edad",
        int(df["Age"].min()),
        int(df["Age"].max()),
        (int(df["Age"].min()), int(df["Age"].max()))
    )

    salary_range = st.slider(
        "Salario Mensual (USD)",
        int(df["MonthlyIncome"].min()),
        int(df["MonthlyIncome"].max()),
        (int(df["MonthlyIncome"].min()), int(df["MonthlyIncome"].max()))
    )

    st.markdown("---")
    st.markdown(f"<p style='font-size:11px; color:#8A8FAF;'>Fuente: IBM HR Analytics<br>Kaggle Dataset · 1,470 registros</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
dff = df.copy()

if dept_sel != "Todos":
    dff = dff[dff["Department"] == dept_sel]
if gender_sel != "Todos":
    dff = dff[dff["Gender"] == gender_sel]
if overtime_sel == "Con Overtime":
    dff = dff[dff["OverTime"] == "Yes"]
elif overtime_sel == "Sin Overtime":
    dff = dff[dff["OverTime"] == "No"]
if marital_sel != "Todos":
    dff = dff[dff["MaritalStatus"] == marital_sel]

dff = dff[
    (dff["Age"] >= age_range[0]) &
    (dff["Age"] <= age_range[1]) &
    (dff["MonthlyIncome"] >= salary_range[0]) &
    (dff["MonthlyIncome"] <= salary_range[1])
]


# ─────────────────────────────────────────────
# MÉTRICAS CALCULADAS
# ─────────────────────────────────────────────
total_emp       = len(dff)
attrition_n     = (dff["Attrition"] == "Yes").sum()
retention_n     = total_emp - attrition_n
attrition_rate  = round(attrition_n / total_emp * 100, 1) if total_emp > 0 else 0
avg_sal_yes     = int(dff[dff["Attrition"] == "Yes"]["MonthlyIncome"].mean()) if attrition_n > 0 else 0
avg_sal_no      = int(dff[dff["Attrition"] == "No"]["MonthlyIncome"].mean()) if retention_n > 0 else 0
sal_gap         = avg_sal_no - avg_sal_yes
ot_rate         = round(dff[dff["OverTime"] == "Yes"]["AttritionBin"].mean() * 100, 1) if len(dff[dff["OverTime"] == "Yes"]) > 0 else 0
avg_years_att   = round(dff[dff["Attrition"] == "Yes"]["YearsAtCompany"].mean(), 1) if attrition_n > 0 else 0


# ─────────────────────────────────────────────
# LAYOUT — NAVEGACIÓN POR PESTAÑAS
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <p class="main-title">📊 Dashboard de Retención de Talento Humano</p>
  <p class="main-subtitle">IBM HR Analytics · Análisis de rotación laboral · {total_emp:,} empleados filtrados</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Resumen General",
    "👥 Perfil del Empleado",
    "💼 Factores de Riesgo",
    "📋 Conclusiones"
])


# ═══════════════════════════════════════════════════════════
# TAB 1 — RESUMEN GENERAL
# ═══════════════════════════════════════════════════════════
with tab1:

    # ── KPI CARDS (patrón Z — primer punto de atención) ──
    st.markdown('<p class="section-title">Indicadores Clave de Desempeño</p>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    color_rate = C_ATTRITION if attrition_rate > 15 else C_ACCENT

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">Total Empleados</p>
          <p class="kpi-value" style="color:{C_GREEN};">{total_emp:,}</p>
          <p class="kpi-sub">registros analizados</p>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">Tasa de Attrition</p>
          <p class="kpi-value" style="color:{color_rate};">{attrition_rate}%</p>
          <p class="kpi-sub">{attrition_n} empleados se fueron</p>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">Salario — Rotan</p>
          <p class="kpi-value" style="color:{C_ATTRITION};">${avg_sal_yes:,}</p>
          <p class="kpi-sub">promedio mensual</p>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">Salario — Retienen</p>
          <p class="kpi-value" style="color:{C_RETENTION};">${avg_sal_no:,}</p>
          <p class="kpi-sub">brecha: ${sal_gap:,}</p>
        </div>""", unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">Attrition c/ Overtime</p>
          <p class="kpi-value" style="color:{C_ATTRITION};">{ot_rate}%</p>
          <p class="kpi-sub">vs {round(dff[dff["OverTime"]=="No"]["AttritionBin"].mean()*100,1)}% sin overtime</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FILA 2: Attrition por Departamento + Distribución general ──
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown('<p class="section-title">Tasa de Attrition por Departamento</p>', unsafe_allow_html=True)

        dept_data = (
            dff.groupby("Department")
            .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
            .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
            .sort_values("rate", ascending=True)
            .reset_index()
        )

        colors_dept = [C_ATTRITION if r > 15 else C_RETENTION for r in dept_data["rate"]]

        fig_dept = go.Figure(go.Bar(
            y=dept_data["Department"],
            x=dept_data["rate"],
            orientation="h",
            marker_color=colors_dept,
            text=[f"{r}%" for r in dept_data["rate"]],
            textposition="outside",
            textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
            hovertemplate="<b>%{y}</b><br>Attrition: %{x}%<extra></extra>"
        ))
        fig_dept.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=60, t=10, b=10),
            height=180,
            xaxis=dict(
                showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
                ticksuffix="%", tickfont=dict(size=11), range=[0, dept_data["rate"].max()+6],
                zeroline=False
            ),
            yaxis=dict(tickfont=dict(size=12)),
            showlegend=False
        )
        st.plotly_chart(fig_dept, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 <b>Sales</b> lidera la rotación ({dept_data[dept_data['Department']=='Sales']['rate'].values[0] if 'Sales' in dept_data['Department'].values else '—'}%).
          El color rojo indica tasa superior al umbral del 15%.
        </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown('<p class="section-title">Composición General</p>', unsafe_allow_html=True)

        fig_donut = go.Figure(go.Pie(
            labels=["Se quedaron", "Se fueron"],
            values=[retention_n, attrition_n],
            hole=0.65,
            marker_colors=[C_RETENTION, C_ATTRITION],
            textinfo="percent",
            textfont=dict(family="Roboto", size=13),
            hovertemplate="<b>%{label}</b><br>%{value} empleados (%{percent})<extra></extra>"
        ))
        fig_donut.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=0, t=10, b=10),
            height=180,
            legend=dict(
                orientation="h", x=0.5, xanchor="center", y=-0.1,
                font=dict(size=12)
            ),
            annotations=[dict(
                text=f"<b>{attrition_rate}%</b><br>Attrition",
                x=0.5, y=0.5, font=dict(size=14, family="Roboto", color=C_ATTRITION),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── FILA 3: Attrition por Job Role ──
    st.markdown('<p class="section-title">Tasa de Attrition por Rol</p>', unsafe_allow_html=True)

    role_data = (
        dff.groupby("JobRole")
        .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
        .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
        .sort_values("rate", ascending=True)
        .reset_index()
    )

    role_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in role_data["rate"]]

    fig_role = go.Figure(go.Bar(
        y=role_data["JobRole"],
        x=role_data["rate"],
        orientation="h",
        marker_color=role_colors,
        text=[f"{r}%  (n={n})" for r, n in zip(role_data["rate"], role_data["total"])],
        textposition="outside",
        textfont=dict(family="Roboto", size=11, color=C_TEXT_MAIN),
        hovertemplate="<b>%{y}</b><br>Attrition: %{x}%<extra></extra>"
    ))
    fig_role.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto", color=C_TEXT_MAIN),
        margin=dict(l=0, r=120, t=10, b=10),
        height=280,
        xaxis=dict(
            showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
            ticksuffix="%", tickfont=dict(size=11),
            range=[0, role_data["rate"].max() + 10], zeroline=False
        ),
        yaxis=dict(tickfont=dict(size=11)),
        showlegend=False
    )

    # Línea de referencia — promedio
    fig_role.add_vline(
        x=attrition_rate, line_dash="dot", line_color=C_TEXT_MUTED, line_width=1.5,
        annotation_text=f"Promedio: {attrition_rate}%",
        annotation_font=dict(color=C_TEXT_MUTED, size=11)
    )
    st.plotly_chart(fig_role, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 2 — PERFIL DEL EMPLEADO
# ═══════════════════════════════════════════════════════════
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Attrition por Grupo de Edad</p>', unsafe_allow_html=True)

        age_data = (
            dff.groupby("AgeBin", observed=True)
            .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
            .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
            .reset_index()
        )

        age_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in age_data["rate"]]

        fig_age = go.Figure(go.Bar(
            x=age_data["AgeBin"].astype(str),
            y=age_data["rate"],
            marker_color=age_colors,
            text=[f"{r}%" for r in age_data["rate"]],
            textposition="outside",
            textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
            hovertemplate="<b>%{x}</b><br>Attrition: %{y}%<extra></extra>"
        ))
        fig_age.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=0, t=20, b=0),
            height=280,
            xaxis=dict(title="Grupo de edad", tickfont=dict(size=11), zeroline=False),
            yaxis=dict(
                title="Tasa de attrition (%)",
                showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
                ticksuffix="%", tickfont=dict(size=11),
                range=[0, age_data["rate"].max() + 8]
            ),
            showlegend=False
        )
        fig_age.add_hline(y=attrition_rate, line_dash="dot", line_color=C_TEXT_MUTED, line_width=1.5)
        st.plotly_chart(fig_age, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 Los empleados jóvenes <b>18-25 años</b> rotan casi el doble del promedio ({age_data[age_data['AgeBin']=='18-25']['rate'].values[0] if '18-25' in age_data['AgeBin'].astype(str).values else '—'}%).
          Son el segmento de mayor riesgo.
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-title">Attrition por Estado Civil</p>', unsafe_allow_html=True)

        ms_data = (
            dff.groupby("MaritalStatus")
            .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
            .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
            .sort_values("rate", ascending=True)
            .reset_index()
        )

        ms_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in ms_data["rate"]]

        fig_ms = go.Figure(go.Bar(
            y=ms_data["MaritalStatus"],
            x=ms_data["rate"],
            orientation="h",
            marker_color=ms_colors,
            text=[f"{r}%" for r in ms_data["rate"]],
            textposition="outside",
            textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
            hovertemplate="<b>%{y}</b><br>Attrition: %{x}%<extra></extra>"
        ))
        fig_ms.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=60, t=20, b=0),
            height=280,
            xaxis=dict(
                showgrid=True, gridcolor=C_BORDER, ticksuffix="%",
                tickfont=dict(size=11), range=[0, ms_data["rate"].max() + 6], zeroline=False
            ),
            yaxis=dict(tickfont=dict(size=12)),
            showlegend=False
        )
        st.plotly_chart(fig_ms, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 Empleados <b>solteros</b> tienen una tasa 2.5x mayor que los divorciados.
          La falta de compromisos personales facilita el cambio de trabajo.
        </div>""", unsafe_allow_html=True)

    # ── Frecuencia de viajes ──
    st.markdown('<p class="section-title">Attrition por Frecuencia de Viajes de Negocio</p>', unsafe_allow_html=True)

    travel_data = (
        dff.groupby("BusinessTravel")
        .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
        .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
        .sort_values("rate", ascending=True)
        .reset_index()
    )

    travel_labels = {
        "Non-Travel": "Sin viajes",
        "Travel_Rarely": "Viajes ocasionales",
        "Travel_Frequently": "Viajes frecuentes"
    }
    travel_data["Label"] = travel_data["BusinessTravel"].map(travel_labels)
    travel_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in travel_data["rate"]]

    fig_travel = go.Figure(go.Bar(
        y=travel_data["Label"],
        x=travel_data["rate"],
        orientation="h",
        marker_color=travel_colors,
        text=[f"{r}%" for r in travel_data["rate"]],
        textposition="outside",
        textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
        hovertemplate="<b>%{y}</b><br>Attrition: %{x}%<extra></extra>"
    ))
    fig_travel.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto", color=C_TEXT_MAIN),
        margin=dict(l=0, r=60, t=10, b=10),
        height=180,
        xaxis=dict(
            showgrid=True, gridcolor=C_BORDER, ticksuffix="%",
            tickfont=dict(size=11), range=[0, travel_data["rate"].max() + 6], zeroline=False
        ),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )
    fig_travel.add_vline(x=attrition_rate, line_dash="dot", line_color=C_TEXT_MUTED, line_width=1.5)
    st.plotly_chart(fig_travel, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 3 — FACTORES DE RIESGO
# ═══════════════════════════════════════════════════════════
with tab3:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Satisfacción Laboral vs Attrition</p>', unsafe_allow_html=True)

        sat_data = (
            dff.groupby("SatisfaccionLabel")
            .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
            .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
            .reset_index()
        )
        # Ordenar lógicamente
        sat_order = ["Baja (1)", "Media-baja (2)", "Media-alta (3)", "Alta (4)"]
        sat_data = sat_data.set_index("SatisfaccionLabel").reindex(sat_order).reset_index()
        sat_data = sat_data.dropna(subset=["rate"])

        sat_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in sat_data["rate"]]

        fig_sat = go.Figure(go.Bar(
            x=sat_data["SatisfaccionLabel"],
            y=sat_data["rate"],
            marker_color=sat_colors,
            text=[f"{r}%" for r in sat_data["rate"]],
            textposition="outside",
            textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
            hovertemplate="<b>%{x}</b><br>Attrition: %{y}%<extra></extra>"
        ))
        fig_sat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=0, t=20, b=0),
            height=280,
            xaxis=dict(title="Nivel de satisfacción", tickfont=dict(size=11)),
            yaxis=dict(
                title="Tasa de attrition (%)",
                showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
                ticksuffix="%", range=[0, sat_data["rate"].max() + 8], zeroline=False
            ),
            showlegend=False
        )
        fig_sat.add_hline(y=attrition_rate, line_dash="dot", line_color=C_TEXT_MUTED, line_width=1.5)
        st.plotly_chart(fig_sat, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 La <b>satisfacción baja (nivel 1)</b> duplica la probabilidad de rotación frente a
          satisfacción alta. Clara relación inversa entre satisfacción y permanencia.
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-title">Balance Vida-Trabajo vs Attrition</p>', unsafe_allow_html=True)

        wlb_data = (
            dff.groupby("WLBLabel")
            .agg(total=("Attrition", "count"), left=("AttritionBin", "sum"))
            .assign(rate=lambda x: round(x["left"] / x["total"] * 100, 1))
            .reset_index()
        )
        wlb_order = ["Malo (1)", "Regular (2)", "Bueno (3)", "Excelente (4)"]
        wlb_data = wlb_data.set_index("WLBLabel").reindex(wlb_order).reset_index()
        wlb_data = wlb_data.dropna(subset=["rate"])

        wlb_colors = [C_ATTRITION if r >= 20 else (C_ACCENT if r >= 12 else C_RETENTION) for r in wlb_data["rate"]]

        fig_wlb = go.Figure(go.Bar(
            x=wlb_data["WLBLabel"],
            y=wlb_data["rate"],
            marker_color=wlb_colors,
            text=[f"{r}%" for r in wlb_data["rate"]],
            textposition="outside",
            textfont=dict(family="Roboto", size=12, color=C_TEXT_MAIN),
            hovertemplate="<b>%{x}</b><br>Attrition: %{y}%<extra></extra>"
        ))
        fig_wlb.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto", color=C_TEXT_MAIN),
            margin=dict(l=0, r=0, t=20, b=0),
            height=280,
            xaxis=dict(title="Balance vida-trabajo", tickfont=dict(size=11)),
            yaxis=dict(
                title="Tasa de attrition (%)",
                showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
                ticksuffix="%", range=[0, wlb_data["rate"].max() + 8], zeroline=False
            ),
            showlegend=False
        )
        fig_wlb.add_hline(y=attrition_rate, line_dash="dot", line_color=C_TEXT_MUTED, line_width=1.5)
        st.plotly_chart(fig_wlb, use_container_width=True)

    # ── Ingreso mensual por rol ──
    st.markdown('<p class="section-title">Ingreso Mensual — Distribución por Rol (quienes se quedaron vs. quienes se fueron)</p>', unsafe_allow_html=True)

    fig_income = go.Figure()

    for att_val, color, label in [("No", C_RETENTION, "Se quedaron"), ("Yes", C_ATTRITION, "Se fueron")]:
        sub = dff[dff["Attrition"] == att_val]
        if len(sub) == 0:
            continue
        income_role = sub.groupby("JobRole")["MonthlyIncome"].median().sort_values(ascending=True)

        fig_income.add_trace(go.Bar(
            y=income_role.index,
            x=income_role.values,
            name=label,
            orientation="h",
            marker_color=color,
            opacity=0.85,
            hovertemplate=f"<b>%{{y}}</b><br>{label}: $%{{x:,.0f}}<extra></extra>"
        ))

    fig_income.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto", color=C_TEXT_MAIN),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        barmode="group",
        xaxis=dict(
            title="Ingreso Mensual (USD)",
            showgrid=True, gridcolor=C_BORDER, gridwidth=0.5,
            tickprefix="$", tickfont=dict(size=11), zeroline=False
        ),
        yaxis=dict(tickfont=dict(size=11)),
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=1.08,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    st.plotly_chart(fig_income, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      🔴 En todos los roles, el ingreso mediano de quienes <b>se fueron</b> (rojo) es menor al de quienes
      <b>se quedaron</b> (azul). La brecha salarial promedio es de <b>${sal_gap:,}/mes</b>.
      El salario es un predictor clave de retención.
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TAB 4 — CONCLUSIONES
# ═══════════════════════════════════════════════════════════
with tab4:

    st.markdown('<p class="section-title">Hallazgos Principales</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="insight-box">
          🔴 <b>Hallazgo 1 — Salario como predictor clave</b><br><br>
          Los empleados que rotan ganan en promedio <b>${avg_sal_yes:,}/mes</b>, frente a
          <b>${avg_sal_no:,}/mes</b> de quienes permanecen. Una brecha de <b>${sal_gap:,}</b>
          sugiere que la competitividad salarial es el factor más accionable para retener talento.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 <b>Hallazgo 2 — Overtime: factor multiplicador de riesgo</b><br><br>
          Empleados con overtime presentan una tasa de {ot_rate}% frente a
          {round(dff[dff['OverTime']=='No']['AttritionBin'].mean()*100,1)}% sin overtime.
          Esto triplica el riesgo. El agotamiento laboral es un predictor directo de renuncia.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 <b>Hallazgo 3 — Sales Representative: rol crítico</b><br><br>
          Con una tasa de attrition cercana al 40%, los representantes de ventas requieren
          atención prioritaria. Su rotación impacta directamente los ingresos de la organización.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-box positive">
          🟢 <b>Hallazgo 4 — Empleados mayores de 35: núcleo estable</b><br><br>
          Los grupos de 36-45 y 46-55 años presentan las tasas más bajas (9.2% y 11.5%).
          Estos empleados representan el talento senior consolidado de la organización.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
          🔴 <b>Hallazgo 5 — Satisfacción laboral: palanca de gestión</b><br><br>
          Empleados con satisfacción nivel 1 rotan al 22.8% vs 11.3% con nivel 4.
          Mejorar la satisfacción es una intervención de bajo costo y alto impacto.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box positive">
          🟢 <b>Recomendación para la organización</b><br><br>
          Priorizar: (1) revisión salarial en roles de alto riesgo, (2) política de control de
          overtime, (3) programas de satisfacción para empleados jóvenes solteros,
          (4) reducción de viajes frecuentes o compensación adicional.
        </div>
        """, unsafe_allow_html=True)

    # ── Tabla resumen ──
    st.markdown('<p class="section-title">Tabla Resumen — Perfil del Empleado en Riesgo</p>', unsafe_allow_html=True)

    risk_data = {
        "Factor": [
            "Rol de trabajo",
            "Departamento",
            "Edad",
            "Estado civil",
            "Overtime",
            "Satisfacción laboral",
            "Viajes de negocio",
            "Salario mensual"
        ],
        "Alto Riesgo (Rota más)": [
            "Sales Representative (39.8%)",
            "Sales (20.6%)",
            "18-25 años (34.8%)",
            "Soltero (25.5%)",
            "Con overtime (30.5%)",
            "Baja — nivel 1 (22.8%)",
            "Frecuentes (24.9%)",
            "< $3,000 / mes"
        ],
        "Bajo Riesgo (Retención alta)": [
            "Research Director (2.5%)",
            "R&D (13.8%)",
            "36-45 años (9.2%)",
            "Divorciado (10.1%)",
            "Sin overtime (10.4%)",
            "Alta — nivel 4 (11.3%)",
            "Sin viajes (8.0%)",
            "> $7,000 / mes"
        ]
    }

    risk_df = pd.DataFrame(risk_data)
    st.dataframe(
        risk_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Factor": st.column_config.TextColumn("Factor", width="medium"),
            "Alto Riesgo (Rota más)": st.column_config.TextColumn("🔴 Alto Riesgo", width="large"),
            "Bajo Riesgo (Retención alta)": st.column_config.TextColumn("🔵 Bajo Riesgo", width="large"),
        }
    )
