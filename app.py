import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Конфигурация страницы Streamlit ---
st.set_page_config(
    page_title="LXD & EdTech Health Audit Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. ГЕНЕРАЦИЯ ДАННЫХ (3 КУРСА × 3 ПОТОКА + МОДУЛЬНАЯ ТЕЛЕМЕТРИЯ)
# ==============================================================================
@st.cache_data
def load_all_audit_data():
    # 1.1. Когортные данные (3 курса по 3 потока, когорты 12-15 человек)
    cohorts_raw = [
        # Курс 1: Рескилл B2C — Data Science с нуля
        # Риски: потеря контроля, порог 3 ошибок, падение в безнадежность
        {
            "product": "Data Science с нуля (Рескилл B2C)",
            "product_type": "Рескилл B2C",
            "cohort_num": 1, "cohort": "Поток 1", "enrolled": 15,
            "cr": 0.60, "a_task": 0.80, "r_market": 0.92,
            "salary_in": 65000, "salary_market": 115000, "course_price": 130000,
            "study_hours": 180, "search_months": 3.0, "dev_cost": 900000, "margin_per_student": 35000
        },
        {
            "product": "Data Science с нуля (Рескилл B2C)",
            "product_type": "Рескилл B2C",
            "cohort_num": 2, "cohort": "Поток 2", "enrolled": 14,
            "cr": 0.50, "a_task": 0.71, "r_market": 0.88,
            "salary_in": 68000, "salary_market": 115000, "course_price": 130000,
            "study_hours": 195, "search_months": 3.5, "dev_cost": 900000, "margin_per_student": 35000
        },
        {
            "product": "Data Science с нуля (Рескилл B2C)",
            "product_type": "Рескилл B2C",
            "cohort_num": 3, "cohort": "Поток 3", "enrolled": 15,
            "cr": 0.40, "a_task": 0.67, "r_market": 0.85,
            "salary_in": 64000, "salary_market": 115000, "course_price": 130000,
            "study_hours": 210, "search_months": 4.0, "dev_cost": 900000, "margin_per_student": 35000
        },

        # Курс 2: Апскилл B2C — Middle Frontend (React/TS)
        # Риски: эффект обращения экспертизы, скука, потеря ценности от банальной теории
        {
            "product": "Middle Frontend (Апскилл B2C)",
            "product_type": "Апскилл B2C",
            "cohort_num": 1, "cohort": "Поток 1", "enrolled": 12,
            "cr": 0.75, "a_task": 0.89, "r_market": 0.95,
            "salary_in": 140000, "salary_market": 210000, "course_price": 95000,
            "study_hours": 90, "search_months": 1.5, "dev_cost": 650000, "margin_per_student": 40000
        },
        {
            "product": "Middle Frontend (Апскилл B2C)",
            "product_type": "Апскилл B2C",
            "cohort_num": 2, "cohort": "Поток 2", "enrolled": 12,
            "cr": 0.75, "a_task": 0.78, "r_market": 0.92,
            "salary_in": 145000, "salary_market": 210000, "course_price": 95000,
            "study_hours": 95, "search_months": 2.0, "dev_cost": 650000, "margin_per_student": 40000
        },
        {
            "product": "Middle Frontend (Апскилл B2C)",
            "product_type": "Апскилл B2C",
            "cohort_num": 3, "cohort": "Поток 3", "enrolled": 13,
            "cr": 0.69, "a_task": 0.67, "r_market": 0.90,
            "salary_in": 142000, "salary_market": 210000, "course_price": 95000,
            "study_hours": 100, "search_months": 2.2, "dev_cost": 650000, "margin_per_student": 40000
        },

        # Курс 3: Корпоративное B2B / B2G — Корпоративная аналитика данных
        # Риски: трение софта, саботаж, бинарность критериев, иллюзия доходимости
        {
            "product": "Корпоративная аналитика (B2B)",
            "product_type": "B2B / B2G",
            "cohort_num": 1, "cohort": "Поток 1", "enrolled": 15,
            "cr": 0.87, "a_task": 0.54, "r_market": 0.85,
            "salary_in": 80000, "salary_market": 110000, "course_price": 85000,
            "study_hours": 60, "search_months": 0.0, "dev_cost": 500000, "margin_per_student": 30000
        },
        {
            "product": "Корпоративная аналитика (B2B)",
            "product_type": "B2B / B2G",
            "cohort_num": 2, "cohort": "Поток 2", "enrolled": 14,
            "cr": 0.86, "a_task": 0.42, "r_market": 0.82,
            "salary_in": 82000, "salary_market": 110000, "course_price": 85000,
            "study_hours": 65, "search_months": 0.0, "dev_cost": 500000, "margin_per_student": 30000
        },
        {
            "product": "Корпоративная аналитика (B2B)",
            "product_type": "B2B / B2G",
            "cohort_num": 3, "cohort": "Поток 3", "enrolled": 15,
            "cr": 0.80, "a_task": 0.33, "r_market": 0.80,
            "salary_in": 85000, "salary_market": 110000, "course_price": 85000,
            "study_hours": 70, "search_months": 0.0, "dev_cost": 500000, "margin_per_student": 30000
        }
    ]
    df_c = pd.DataFrame(cohorts_raw)

    # Расчет ядра здоровья: HI_core = CR * A_task * R_market
    df_c["hi_core"] = df_c["cr"] * df_c["a_task"] * df_c["r_market"]
    df_c["competence_output"] = df_c["cr"] * df_c["a_task"]

    # Расчет срока окупаемости для студента (PP_user)
    hourly_rate = df_c["salary_in"] / 160.0
    student_invest = df_c["course_price"] + (df_c["study_hours"] * hourly_rate)
    salary_delta = np.maximum(df_c["salary_market"] - df_c["salary_in"], 5000)
    expected_gain = salary_delta * df_c["hi_core"]
    df_c["pp_user_months"] = np.round(df_c["search_months"] + (student_invest / expected_gain), 1)

    # Срок окупаемости разработки для бизнеса (PP_biz в потоках)
    df_c["pp_biz_cohorts"] = np.round(df_c["dev_cost"] / (df_c["enrolled"] * df_c["margin_per_student"]), 1)

    def calc_status(hi):
        if hi >= 0.50:
            return "🟢 Здоровый"
        elif hi >= 0.25:
            return "🟡 Зона риска"
        return "🔴 Критический"

    df_c["status"] = df_c["hi_core"].apply(calc_status)

    # 1.2. Помодульные данные и телеметрия практик для последнего (3-го) потока
    modules_raw = [
        # Data Science (Поток 3)
        {
            "product": "Data Science с нуля (Рескилл B2C)", "cohort": "Поток 3",
            "module_num": 1, "module_name": "M1: Введение и основы Python",
            "cor": 0.93, "rushed_count": 1, "frag_count": 0, "depleted_count": 0,
            "error_loops_3": 0, "mentor_sla_hours": 14, "csi_score": 4.8,
            "primary_lxd_param": "Субъективный контроль (в норме)",
            "root_cause": "Быстрый вход в практику, достигнута 'ранняя победа' в первые 15 минут."
        },
        {
            "product": "Data Science с нуля (Рескилл B2C)", "cohort": "Поток 3",
            "module_num": 2, "module_name": "M2: Алгоритмы и векторные вычисления",
            "cor": 0.67, "rushed_count": 5, "frag_count": 3, "depleted_count": 3,
            "error_loops_3": 6, "mentor_sla_hours": 36, "csi_score": 3.6,
            "primary_lxd_param": "Субъективный контроль & Эмоциональные срывы",
            "root_cause": "Высокая интерактивность формул. Нет scaffolding (подсказок на 2-й ошибке). Студенты делают по 3+ ошибок, смещают локус на 'я не технарь' и бросают модуль."
        },
        {
            "product": "Data Science с нуля (Рескилл B2C)", "cohort": "Поток 3",
            "module_num": 3, "module_name": "M3: Машинное обучение: классификация",
            "cor": 0.53, "rushed_count": 4, "frag_count": 2, "depleted_count": 4,
            "error_loops_3": 5, "mentor_sla_hours": 28, "csi_score": 3.8,
            "primary_lxd_param": "Посторонняя когнитивная нагрузка",
            "root_cause": "Перегрузка теорией без стартовых шаблонов кода; барьер чистого листа."
        },
        {
            "product": "Data Science с нуля (Рескилл B2C)", "cohort": "Поток 3",
            "module_num": 4, "module_name": "M4: Аутентичный выпускной кейс",
            "cor": 0.40, "rushed_count": 3, "frag_count": 1, "depleted_count": 2,
            "error_loops_3": 3, "mentor_sla_hours": 20, "csi_score": 4.1,
            "primary_lxd_param": "Субъективный контроль",
            "root_cause": "Непрозрачные критерии сдачи выпускного проекта; студенты не понимают, по каким признакам оценивается результат."
        },

        # Middle Frontend (Поток 3)
        {
            "product": "Middle Frontend (Апскилл B2C)", "cohort": "Поток 3",
            "module_num": 1, "module_name": "M1: Архитектура React 19",
            "cor": 0.92, "rushed_count": 1, "frag_count": 0, "depleted_count": 0,
            "error_loops_3": 1, "mentor_sla_hours": 12, "csi_score": 4.7,
            "primary_lxd_param": "Субъективная ценность",
            "root_cause": "Боевой стек, высокий интерес к изучению нового."
        },
        {
            "product": "Middle Frontend (Апскилл B2C)", "cohort": "Поток 3",
            "module_num": 2, "module_name": "M2: Базовый рекап TypeScript",
            "cor": 0.85, "rushed_count": 0, "frag_count": 0, "depleted_count": 1,
            "error_loops_3": 0, "mentor_sla_hours": 16, "csi_score": 3.4,
            "primary_lxd_param": "Субъективная ценность & Посторонняя нагрузка",
            "root_cause": "Эффект обращения экспертизы: мидлам подробно объясняют основы синтаксиса. Это порождает деактивирующую скуку и саботаж выполнения ДЗ."
        },
        {
            "product": "Middle Frontend (Апскилл B2C)", "cohort": "Поток 3",
            "module_num": 3, "module_name": "M3: Оптимизация SSR и рендеринга",
            "cor": 0.77, "rushed_count": 2, "frag_count": 1, "depleted_count": 1,
            "error_loops_3": 2, "mentor_sla_hours": 15, "csi_score": 4.5,
            "primary_lxd_param": "Субъективная ценность",
            "root_cause": "Практика построена на боевом рабочем артефакте."
        },
        {
            "product": "Middle Frontend (Апскилл B2C)", "cohort": "Поток 3",
            "module_num": 4, "module_name": "M4: Production-ready релиз",
            "cor": 0.69, "rushed_count": 2, "frag_count": 0, "depleted_count": 1,
            "error_loops_3": 1, "mentor_sla_hours": 18, "csi_score": 4.6,
            "primary_lxd_param": "Субъективный контроль",
            "root_cause": "Защита рабочего проекта перед ментором."
        },

        # Корпоративная аналитика (Поток 3)
        {
            "product": "Корпоративная аналитика (B2B)", "cohort": "Поток 3",
            "module_num": 1, "module_name": "M1: BI-дашборды и метрики",
            "cor": 1.00, "rushed_count": 1, "frag_count": 0, "depleted_count": 0,
            "error_loops_3": 0, "mentor_sla_hours": 10, "csi_score": 4.9,
            "primary_lxd_param": "Трение среды",
            "root_cause": "Бесшовный запуск веб-среды в браузере."
        },
        {
            "product": "Корпоративная аналитика (B2B)", "cohort": "Поток 3",
            "module_num": 2, "module_name": "M2: Корпоративный SQL и ETL",
            "cor": 0.93, "rushed_count": 2, "frag_count": 1, "depleted_count": 1,
            "error_loops_3": 4, "mentor_sla_hours": 26, "csi_score": 3.7,
            "primary_lxd_param": "Трение среды & Субъективный контроль",
            "root_cause": "Конфликт прав локального ПО на корпоративных ноутбуках и небинарные критерии сдачи тестов."
        },
        {
            "product": "Корпоративная аналитика (B2B)", "cohort": "Поток 3",
            "module_num": 3, "module_name": "M3: Продвинутые когорты",
            "cor": 0.87, "rushed_count": 1, "frag_count": 2, "depleted_count": 1,
            "error_loops_3": 2, "mentor_sla_hours": 18, "csi_score": 4.0,
            "primary_lxd_param": "Субъективный контроль",
            "root_cause": "Разрозненность справочных шаблонов."
        },
        {
            "product": "Корпоративная аналитика (B2B)", "cohort": "Поток 3",
            "module_num": 4, "module_name": "M4: Самостоятельный итоговый проект",
            "cor": 0.80, "rushed_count": 1, "frag_count": 4, "depleted_count": 2,
            "error_loops_3": 7, "mentor_sla_hours": 22, "csi_score": 3.2,
            "primary_lxd_param": "Субъективный контроль (Иллюзия доходимости)",
            "root_cause": "Студенты формально прошли курс на подсказках куратора, но без готовых шаблонов решить задачу не могут: A_task упал до 33%."
        }
    ]
    df_m = pd.DataFrame(modules_raw)
    return df_c, df_m

df_cohorts, df_modules = load_all_audit_data()

# ==============================================================================
# 2. БОКОВАЯ ПАНЕЛЬ (НАВИГАЦИЯ И ФИЛЬТРЫ)
# ==============================================================================
st.sidebar.title("⚙️ Навигация и фильтры")

cohort_depth = st.sidebar.slider(
    "Количество потоков в анализе:",
    min_value=1,
    max_value=3,
    value=3,
    help="Глубина скользящего окна анализа когорт"
)

df_filtered_cohorts = df_cohorts[df_cohorts["cohort_num"] <= cohort_depth].copy()
available_products = df_filtered_cohorts["product"].unique().tolist()

selected_product = st.sidebar.selectbox(
    "Выберите курс для детального аудита:",
    available_products
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Пороги здоровья ($HI_{\\text{core}}$):**
* 🟢 **Здоровый:** $\ge 0.500$
* 🟡 **Зона риска:** $0.250 - 0.499$
* 🔴 **Критический:** $< 0.250$

**Срок окупаемости ($PP_{\\text{user}}$):**
* 🟢 $\le 12$ мес. (Высокая ценность)
* 🟡 $13–18$ мес. (Допустимо)
* 🔴 $> 18$ мес. (Экономический тупик)
""")

# ==============================================================================
# 3. ОСНОВНОЙ ЭКРАН ДАШБОРДА
# ==============================================================================
st.title("🎓 Система аудита образовательных продуктов (LXD & Health Monitor)")
st.caption("Методическое ядро ($HI_{\\text{core}}$) ➔ Окупаемость ($PP_{\\text{user}}, PP_{\\text{biz}}$) ➔ Архитектура опыта (LXD-модель)")

tab1, tab2, tab3 = st.tabs([
    "📌 Портфель продуктов (C-Level)",
    "⚡ Пульс потока (In-Flight)",
    "🔍 LXD-диагностика модуля"
])

# ==============================================================================
# ВКЛАДКА 1: ПОРТФЕЛЬ ПРОДУКТОВ (C-LEVEL / СТРАТЕГИЧЕСКИЙ КОНТУР)
# ==============================================================================
with tab1:
    st.subheader(f"📊 Сводный статус здоровья портфеля (Потоки 1 – {cohort_depth})")

    summary_records = []
    for p in available_products:
        p_sub = df_filtered_cohorts[df_filtered_cohorts["product"] == p]
        latest_row = p_sub.iloc[-1]
        prev_row = p_sub.iloc[-2] if len(p_sub) > 1 else latest_row

        summary_records.append({
            "Курс": p,
            "Сегмент": latest_row["product_type"],
            "Статус": latest_row["status"],
            "Текущий HI": latest_row["hi_core"],
            "Динамика HI": latest_row["hi_core"] - prev_row["hi_core"],
            "Сквозной выход": round(latest_row["competence_output"] * 100, 1),
            "PP студента (мес.)": latest_row["pp_user_months"],
            "PP бизнеса (потоков)": latest_row["pp_biz_cohorts"],
            "Тренд HI": p_sub["hi_core"].tolist()
        })
    df_summary = pd.DataFrame(summary_records)

    st.dataframe(
        df_summary,
        column_config={
            "Текущий HI": st.column_config.NumberColumn(format="%.3f"),
            "Динамика HI": st.column_config.NumberColumn(format="%+.3f"),
            "Сквозной выход": st.column_config.ProgressColumn(
                "Сквозной выход (CR × A)",
                format="%d%%",
                min_value=0,
                max_value=100,
                help="Реальная доля от всех купивших курс, кто подтвердил навык на аутентичном кейсе"
            ),
            "PP студента (мес.)": st.column_config.NumberColumn(format="%.1f мес."),
            "PP бизнеса (потоков)": st.column_config.NumberColumn(format="%.1f"),
            "Тренд HI": st.column_config.LineChartColumn(
                "Тренд HI",
                y_min=0.0,
                y_max=0.7
            )
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        st.markdown("#### 📈 Динамика Health Index по потокам")
        fig_trend = px.line(
            df_filtered_cohorts,
            x="cohort",
            y="hi_core",
            color="product",
            markers=True,
            labels={"hi_core": "Health Index", "cohort": "Поток", "product": "Курс"}
        )
        fig_trend.add_hrect(y0=0.50, y1=1.00, fillcolor="rgba(46, 204, 113, 0.08)", line_width=0, annotation_text="Зеленая зона (≥ 0.50)")
        fig_trend.add_hrect(y0=0.25, y1=0.50, fillcolor="rgba(241, 196, 15, 0.08)", line_width=0, annotation_text="Желтая зона")
        fig_trend.add_hrect(y0=0.00, y1=0.25, fillcolor="rgba(231, 76, 60, 0.08)", line_width=0, annotation_text="Красная зона (< 0.25)")
        fig_trend.update_layout(
            yaxis_range=[0, 0.75],
            hovermode="x unified",
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_chart2:
        st.markdown(f"#### 🎯 Матрица качества (Поток {cohort_depth})")
        latest_cohorts_slice = df_filtered_cohorts[df_filtered_cohorts["cohort_num"] == cohort_depth].copy()

        fig_matrix = px.scatter(
            latest_cohorts_slice,
            x="cr",
            y="a_task",
            size=[r * 45 for r in latest_cohorts_slice["r_market"]],
            color="product_type",
            text="product",
            labels={"cr": "Доходимость (CR)", "a_task": "Сдача кейса (A_task)", "product_type": "Тип курса"},
            hover_data={"hi_core": ":.3f", "pp_user_months": ":.1f"}
        )
        fig_matrix.add_hline(y=0.60, line_dash="dot", line_color="red", annotation_text="Порог A_task (60%)")
        fig_matrix.update_traces(textposition="top center")
        fig_matrix.update_layout(
            xaxis=dict(range=[0.3, 1.0], tickformat=".0%"),
            yaxis=dict(range=[0.2, 1.0], tickformat=".0%"),
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        st.caption("Размер маркера отражает $R_{\\text{market}}$ (актуальность стека на рынке).")

# ==============================================================================
# ВКЛАДКА 2: ПУЛЬС ПОТОКА (IN-FLIGHT / ОПЕРАТИВНЫЙ КОНТУР)
# ==============================================================================
with tab2:
    st.subheader(f"⚡ Тактический пульс потока: {selected_product}")
    selected_prod_modules = df_modules[df_modules["product"] == selected_product].sort_values("module_num")

    # Операционные алерты закрытой петли
    alert_cols = st.columns(3)
    total_error_loops = int(selected_prod_modules["error_loops_3"].sum())
    max_sla = int(selected_prod_modules["mentor_sla_hours"].max())
    critical_modules_count = len(selected_prod_modules[selected_prod_modules["depleted_count"] >= 2])

    alert_cols[0].metric(
        "Петли ≥ 3 ошибок (Срыв контроля)",
        f"{total_error_loops} инцидентов",
        delta="Требуется адаптивный scaffolding" if total_error_loops > 4 else "В норме",
        delta_color="inverse"
    )
    alert_cols[1].metric(
        "Макс. SLA проверки заданий ментором",
        f"{max_sla} часов",
        delta="Превышен порог нормы (24 ч)" if max_sla > 24 else "В норме (< 24 ч)",
        delta_color="inverse"
    )
    alert_cols[2].metric(
        "Модули с риском выгорания (Energy)",
        f"{critical_modules_count} модуля",
        delta="≥ 2 истощенных студентов" if critical_modules_count > 0 else "Нет риска",
        delta_color="inverse"
    )

    st.markdown("---")

    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        st.markdown("#### 📉 Карта удержания по модулям (Drop-off Map)")
        fig_cor = px.bar(
            selected_prod_modules,
            x="module_name",
            y="cor",
            text=[f"{v:.0%}" for v in selected_prod_modules["cor"]],
            color="cor",
            color_continuous_scale="Blues_r",
            labels={"cor": "Удержание (COR)", "module_name": "Модуль"}
        )
        fig_cor.update_layout(
            yaxis=dict(range=[0, 1.1], tickformat=".0%"),
            showlegend=False,
            height=370,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_cor, use_container_width=True)

    with col_v2:
        st.markdown("#### 🚨 Сигналы MHI и телеметрия платформы")
        heatmap_data = selected_prod_modules[[
            "module_name", "rushed_count", "frag_count", "depleted_count", "error_loops_3"
        ]].copy()
        heatmap_data.columns = ["Модуль", "Pacing: Спешка", "Cohesion: Хаос", "Energy: Истощение", "Петли ≥ 3 ошибок"]

        st.dataframe(
            heatmap_data.set_index("Модуль"),
            column_config={
                "Pacing: Спешка": st.column_config.NumberColumn(help="≥ 3 ответов в когорте: перегруз объемом"),
                "Cohesion: Хаос": st.column_config.NumberColumn(help="≥ 2 ответов: методический разрыв сценария"),
                "Energy: Истощение": st.column_config.NumberColumn(help="≥ 2 ответов: риск тихого оттока"),
                "Петли ≥ 3 ошибок": st.column_config.NumberColumn(help="Серии безуспешных отправок без смены контекста")
            },
            use_container_width=True
        )
        st.caption("Правило малых когорт: пороги настроены на абсолютное число студентов (10–15 чел. в группе).")

# ==============================================================================
# ВКЛАДКА 3: LXD-ДИАГНОСТИКА МОДУЛЯ (ROOT CAUSE ANALYSIS)
# ==============================================================================
with tab3:
    st.subheader(f"🔍 LXD-диагностика и выработка решений: {selected_product}")

    selected_mod_name = st.selectbox(
        "Выберите модуль для расследования первопричины сбоя:",
        selected_prod_modules["module_name"].tolist(),
        index=1 if len(selected_prod_modules) > 1 else 0
    )

    mod_info = selected_prod_modules[selected_prod_modules["module_name"] == selected_mod_name].iloc[0]

    with st.container(border=True):
        st.markdown(f"### Диагностическая карточка: **{mod_info['module_name']}**")
        st.markdown(f"**Ведущий фактор сбоя в среде:** `{mod_info['primary_lxd_param']}`")
        st.info(f"**Аналитическое заключение (Root Cause):** {mod_info['root_cause']}")

        c_diag1, c_diag2 = st.columns(2)

        with c_diag1:
            st.markdown("#### 📋 Статус по 5 параметрам модели LXD:")
            
            p1_status = "🔴 Перегруз" if mod_info["rushed_count"] >= 3 else "🟢 В норме"
            p2_status = "🔴 Высокое трение" if mod_info["mentor_sla_hours"] > 24 else "🟢 Низкое"
            p3_status = "🔴 Контроль разрушен" if mod_info["frag_count"] >= 2 else "🟢 Устойчив"
            p4_status = f"🟡 CSI = {mod_info['csi_score']}" if mod_info["csi_score"] < 4.0 else f"🟢 CSI = {mod_info['csi_score']}"
            p5_status = "🔴 Порог срыва" if mod_info["error_loops_3"] >= 3 else "🟢 Стабильно"

            st.markdown(f"""
            1. **Посторонняя когнитивная нагрузка:** {p1_status}  
               *(Жалобы на спешку: {mod_info['rushed_count']} чел.)*
            2. **Трение среды и барьеры действия:** {p2_status}  
               *(SLA проверки ревью: {mod_info['mentor_sla_hours']} ч)*
            3. **Субъективный контроль:** {p3_status}  
               *(Разрыв логики Cohesion: {mod_info['frag_count']} чел.)*
            4. **Субъективная ценность:** {p4_status} / 5.0  
               *(Оценка CSI и соответствие целевому навыку)*
            5. **Эмоциональная динамика:** {p5_status}  
               *({mod_info['error_loops_3']} петель по ≥ 3 ошибок подряд)*
            """)

        with c_diag2:
            st.markdown("#### 🛠 Предписываемые микро-интервенции (Чек-лист LXD):")
            if "Рескилл" in selected_product:
                st.markdown("""
                * [ ] **Критерий №19 (Scaffolding):** Встроить автоматическую контекстную подсказку на 2-й ошибке подряд, предотвращая сдвиг атрибуции на личность.
                * [ ] **Критерий №28 (Безопасность проб):** Убрать стыдящие экраны («Неверно! Попробуйте снова»), заменить на нейтральный разбор кода.
                * [ ] **Критерий №16 (Критерии приемки):** Опубликовать открытый чек-лист самопроверки до нажатия кнопки сдачи ДЗ.
                * [ ] **Критерий №4 (Справочники):** Разместить шпаргалку синтаксиса непосредственно на экране практического задания.
                """)
            elif "Апскилл" in selected_product:
                st.markdown("""
                * [ ] **Критерий №27 (Защита от скуки):** Внедрить тест экстерната для пропуска базовой теории опытными разработчиками.
                * [ ] **Критерий №4 (Принцип 'с полки'):** Заменить академические лонгриды на лаконичные схемы и памятки без теоретического балласта.
                * [ ] **Критерий №23 (Аутентичность):** Перевести задание на создание реального артефакта в кодовой базе вместо абстрактных упражнений.
                """)
            else:  # B2B / B2G
                st.markdown("""
                * [ ] **Критерий №9 (Нулевые барьеры среды):** Перевести практическое окружение полностью в веб-браузер без локальной установки софта на корпоративные ПК.
                * [ ] **Критерий №16 (Бинарность критериев):** Сформулировать однозначные требования к результату («сдано / не сдано» по чеклисту).
                * [ ] **Критерий №11 (Служебные действия):** Исключить ручное заполнение отчетов и пересылку файлов через сторонние каналы.
                """)
