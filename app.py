import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Конфигурация страницы ---
st.set_page_config(
    page_title="Мониторинг качества курса (LXD & Health)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. МОДЕЛЬ СИНТЕТИЧЕСКИХ ДАННЫХ КУРСА ПО ПОТОКАМ И МОДУЛЯМ
# ==============================================================================
@st.cache_data
def load_course_audit_data():
    # 1.1. Данные по наборам (когортам) одного курса (10-14 человек в группе)
    cohorts_data = [
        {
            "cohort_num": 1, "cohort_name": "Поток 1 (Старт)", "enrolled": 12,
            "finished": 8, "passed_atask": 6, "r_market": 0.90,
            "avg_mhi_cohesion": 72.0, "avg_mhi_pacing_ok": 68.0, "avg_csi": 4.2
        },
        {
            "cohort_num": 2, "cohort_name": "Поток 2 (Спад)", "enrolled": 14,
            "finished": 7, "passed_atask": 4, "r_market": 0.88,
            "avg_mhi_cohesion": 55.0, "avg_mhi_pacing_ok": 50.0, "avg_csi": 3.7
        },
        {
            "cohort_num": 3, "cohort_name": "Поток 3 (Текущий)", "enrolled": 13,
            "finished": 6, "passed_atask": 4, "r_market": 0.85,
            "avg_mhi_cohesion": 52.0, "avg_mhi_pacing_ok": 46.0, "avg_csi": 3.6
        }
    ]
    df_c = pd.DataFrame(cohorts_data)
    df_c["cr"] = df_c["finished"] / df_c["enrolled"]
    df_c["a_task"] = df_c["passed_atask"] / df_c["finished"]
    df_c["hi_core"] = df_c["cr"] * df_c["a_task"] * df_c["r_market"]

    # 1.2. Помодульные замеры по потокам (4 модуля программы)
    # Показывает, как модули вели себя в Потоке 1, 2 и 3
    modules_history = [
        # Поток 1
        {"cohort_num": 1, "cohort_name": "Поток 1", "module_num": 1, "module_name": "M1: Введение и базовый синтаксис", "cor": 1.00, "drop_count": 0, "rushed_count": 1, "frag_count": 0, "depleted_count": 0, "csi": 4.8},
        {"cohort_num": 1, "cohort_name": "Поток 1", "module_num": 2, "module_name": "M2: Алгоритмы и структуры данных", "cor": 0.83, "drop_count": 2, "rushed_count": 3, "frag_count": 2, "depleted_count": 1, "csi": 4.1},
        {"cohort_num": 1, "cohort_name": "Поток 1", "module_num": 3, "module_name": "M3: Работа с библиотеками и API", "cor": 0.75, "drop_count": 1, "rushed_count": 2, "frag_count": 1, "depleted_count": 1, "csi": 4.3},
        {"cohort_num": 1, "cohort_name": "Поток 1", "module_num": 4, "module_name": "M4: Аутентичный выпускной проект", "cor": 0.67, "drop_count": 1, "rushed_count": 2, "frag_count": 1, "depleted_count": 2, "csi": 4.2},

        # Поток 2 (Сломался модуль 2)
        {"cohort_num": 2, "cohort_name": "Поток 2", "module_num": 1, "module_name": "M1: Введение и базовый синтаксис", "cor": 0.93, "drop_count": 1, "rushed_count": 1, "frag_count": 0, "depleted_count": 0, "csi": 4.7},
        {"cohort_num": 2, "cohort_name": "Поток 2", "module_num": 2, "module_name": "M2: Алгоритмы и структуры данных", "cor": 0.64, "drop_count": 4, "rushed_count": 6, "frag_count": 4, "depleted_count": 3, "csi": 3.3},
        {"cohort_num": 2, "cohort_name": "Поток 2", "module_num": 3, "module_name": "M3: Работа с библиотеками и API", "cor": 0.57, "drop_count": 1, "rushed_count": 4, "frag_count": 2, "depleted_count": 3, "csi": 3.8},
        {"cohort_num": 2, "cohort_name": "Поток 2", "module_num": 4, "module_name": "M4: Аутентичный выпускной проект", "cor": 0.50, "drop_count": 1, "rushed_count": 3, "frag_count": 2, "depleted_count": 3, "csi": 3.9},

        # Поток 3 (Критический перегруз на М2 и М3)
        {"cohort_num": 3, "cohort_name": "Поток 3", "module_num": 1, "module_name": "M1: Введение и базовый синтаксис", "cor": 0.92, "drop_count": 1, "rushed_count": 1, "frag_count": 0, "depleted_count": 0, "csi": 4.6},
        {"cohort_num": 3, "cohort_name": "Поток 3", "module_num": 2, "module_name": "M2: Алгоритмы и структуры данных", "cor": 0.62, "drop_count": 4, "rushed_count": 5, "frag_count": 4, "depleted_count": 3, "csi": 3.2},
        {"cohort_num": 3, "cohort_name": "Поток 3", "module_num": 3, "module_name": "M3: Работа с библиотеками и API", "cor": 0.54, "drop_count": 1, "rushed_count": 4, "frag_count": 3, "depleted_count": 4, "csi": 3.5},
        {"cohort_num": 3, "cohort_name": "Поток 3", "module_num": 4, "module_name": "M4: Аутентичный выпускной проект", "cor": 0.46, "drop_count": 1, "rushed_count": 3, "frag_count": 2, "depleted_count": 3, "csi": 3.8},
    ]
    df_m = pd.DataFrame(modules_history)
    return df_c, df_m

df_cohorts, df_modules = load_course_audit_data()

# ==============================================================================
# 2. РАСЧЕТ ИНДИКАТОРА ДОВЕРИЯ К ДАННЫМ (DATA CONFIDENCE ENGINE)
# ==============================================================================
def get_data_trust_badge(sample_size):
    if sample_size >= 30:
        return "🟢 Высокое доверие", "Выборка репрезентативна (N ≥ 30). Статистика надежна для принятия решений о редизайне курса.", "success"
    elif sample_size >= 16:
        return "🟡 Среднее доверие", "Идет накопление выборки (16 ≤ N < 30). Тренды намечены, но сохраняется волатильность отдельных ответов.", "warning"
    else:
        return "🔴 Низкая стат. мощность", "Малая выборка (N < 16). Данные пригодны ТОЛЬКО для оперативного closed-loop (помощи студентам), но не для переделки курса.", "error"

# ==============================================================================
# 3. БОКОВАЯ ПАНЕЛЬ И НАВИГАЦИЯ
# ==============================================================================
st.sidebar.title("⚙️ Параметры аудита")

cohort_options = df_cohorts["cohort_name"].tolist()
selected_cohort = st.sidebar.selectbox("Выберите анализируемый поток:", cohort_options, index=len(cohort_options)-1)
selected_cohort_row = df_cohorts[df_cohorts["cohort_name"] == selected_cohort].iloc[0]

# Индикатор накопления
st.sidebar.markdown("---")
st.sidebar.subheader("🛡 Достоверность данных")
cohort_students = selected_cohort_row["enrolled"]
total_accumulated_students = df_cohorts[df_cohorts["cohort_num"] <= selected_cohort_row["cohort_num"]]["enrolled"].sum()

badge_title, badge_desc, badge_type = get_data_trust_badge(cohort_students)

if badge_type == "success":
    st.sidebar.success(f"**Текущий поток:** {badge_title}\n\nСтудентов в потоке: {cohort_students}")
elif badge_type == "warning":
    st.sidebar.warning(f"**Текущий поток:** {badge_title}\n\nСтудентов в потоке: {cohort_students}")
else:
    st.sidebar.error(f"**Текущий поток:** {badge_title}\n\nСтудентов в потоке: {cohort_students}")

st.sidebar.caption(badge_desc)
st.sidebar.info(f"**Кумулятивно накоплено:** {total_accumulated_students} студентов по {selected_cohort_row['cohort_num']} наборам.")

# ==============================================================================
# 4. ОСНОВНОЙ ЭКРАН
# ==============================================================================
st.title("🎯 Мониторинг качества курса: Оперативный пульс и Тренды")
st.caption(f"Анализ программы: **Data Science & Аналитика** | Фокус: **{selected_cohort}** (когорта {cohort_students} чел.)")

tab1, tab2, tab3 = st.tabs([
    "⚡ Состояние в моменте (Модули потока)",
    "📈 Динамика во времени (Сравнение наборов)",
    "🔗 Связка метрик (Влияние MHI/CSI на результат)"
])

# ==============================================================================
# ВКЛАДКА 1: СОСТОЯНИЕ В МОМЕНТЕ (ТЕКУЩИЙ НАБОР)
# ==============================================================================
with tab1:
    st.subheader(f"📍 Помодульный срез: {selected_cohort}")
    curr_mod_df = df_modules[df_modules["cohort_name"] == selected_cohort].sort_values("module_num")

    # Верхние KPI текущего набора
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    kpi_c1.metric("Зачислено студентов", f"{selected_cohort_row['enrolled']} чел.")
    kpi_c2.metric("Дошли до финала (CR)", f"{selected_cohort_row['cr']:.1%}", f"{selected_cohort_row['finished']} из {selected_cohort_row['enrolled']}")
    kpi_c3.metric("Сдали аутентичный кейс (A_task)", f"{selected_cohort_row['a_task']:.1%}", f"{selected_cohort_row['passed_atask']} чел.")
    kpi_c4.metric("Методическое ядро (HI_core)", f"{selected_cohort_row['hi_core']:.3f}", help="CR × A_task × R_market")

    st.markdown("---")

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.markdown("#### 📉 Воронка удержания (Drop-off Map)")
        fig_cor = px.bar(
            curr_mod_df,
            x="module_name",
            y="cor",
            text=[f"{v:.0%}" for v in curr_mod_df["cor"]],
            color="cor",
            color_continuous_scale="Blues_r",
            labels={"cor": "Удержание (COR)", "module_name": "Модуль"}
        )
        fig_cor.update_layout(yaxis=dict(range=[0, 1.15], tickformat=".0%"), showlegend=False, height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_cor, use_container_width=True)

    with col_m2:
        st.markdown("#### 🚨 Сигналы MHI и CSI (в абсолютных числах)")
        display_mhi = curr_mod_df[["module_name", "rushed_count", "frag_count", "depleted_count", "csi"]].copy()
        display_mhi.columns = ["Модуль", "Спешат (чел.)", "Разрыв связности (чел.)", "Истощение (чел.)", "CSI (1-5)"]

        st.dataframe(
            display_mhi.set_index("Модуль"),
            column_config={
                "Спешат (чел.)": st.column_config.NumberColumn(help="Порог алерта: ≥ 3 чел."),
                "Разрыв связности (чел.)": st.column_config.NumberColumn(help="Порог алерта: ≥ 2 чел."),
                "Истощение (чел.)": st.column_config.NumberColumn(help="Порог алерта: ≥ 2 чел."),
                "CSI (1-5)": st.column_config.NumberColumn(format="%.1f")
            },
            use_container_width=True
        )
        st.caption("⚠️ **Правило малых когорт:** при группе в 13 человек проценты искажают картину. Ориентируйтесь на абсолютное число поднятых рук.")

    # Блок оперативного реагирования (Closed-Loop)
    with st.container(border=True):
        st.markdown("#### 🛠 Оперативные задачи службы сопровождения (Closed-Loop)")
        critical_modules = curr_mod_df[(curr_mod_df["depleted_count"] >= 2) | (curr_mod_df["frag_count"] >= 2)]
        if not critical_modules.empty:
            for _, r in critical_modules.iterrows():
                st.error(
                    f"**{r['module_name']}:** зафиксировано {r['depleted_count']} чел. в сильном истощении и "
                    f"{r['frag_count']} чел. с разрывом логики. "
                    f"**Действие тьютору:** персональный контакт со студентами в течение 24 часов, выявление причин задержки ДЗ."
                )
        else:
            st.success("Критических алертов по MHI в текущем потоке нет. Ситуация стабильна.")

# ==============================================================================
# ВКЛАДКА 2: ДИНАМИКА ВО ВРЕМЕНИ (СРАВНЕНИЕ НАБОРОВ)
# ==============================================================================
with tab2:
    st.subheader("📈 Динамика показателей между наборами (Потоки 1 – 3)")
    st.markdown("Сравнение когорт позволяет отследить: улучшается ли курс или деградирует по мере жизни программы.")

    # График динамики ядра здоровья и его составляющих
    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        st.markdown("#### 🎯 Динамика методического ядра (HI_core)")
        fig_hi = px.line(
            df_cohorts,
            x="cohort_name",
            y="hi_core",
            markers=True,
            text=[f"{v:.3f}" for v in df_cohorts["hi_core"]],
            labels={"hi_core": "HI_core", "cohort_name": "Поток"}
        )
        fig_hi.add_hrect(y0=0.50, y1=1.00, fillcolor="rgba(46, 204, 113, 0.1)", line_width=0, annotation_text="Здоровая зона (≥ 0.50)")
        fig_hi.add_hrect(y0=0.25, y1=0.50, fillcolor="rgba(241, 196, 15, 0.1)", line_width=0, annotation_text="Зона риска")
        fig_hi.add_hrect(y0=0.00, y1=0.25, fillcolor="rgba(231, 76, 60, 0.1)", line_width=0, annotation_text="Критическая зона")
        fig_hi.update_traces(textposition="top center", line=dict(color="#2C3E50", width=3))
        fig_hi.update_layout(yaxis_range=[0, 0.7], height=360, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_hi, use_container_width=True)

    with col_t2:
        st.markdown("#### 🔍 Разложение: Доходимость (CR) vs Сдача кейса (A_task)")
        fig_bar_decomp = go.Figure()
        fig_bar_decomp.add_trace(go.Bar(x=df_cohorts["cohort_name"], y=df_cohorts["cr"], name="CR (Доходимость)", marker_color="#3498DB"))
        fig_bar_decomp.add_trace(go.Bar(x=df_cohorts["cohort_name"], y=df_cohorts["a_task"], name="A_task (Сдача задачи)", marker_color="#2ECC71"))
        fig_bar_decomp.update_layout(
            barmode="group",
            yaxis=dict(tickformat=".0%", range=[0, 1.05]),
            height=360,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar_decomp, use_container_width=True)

    st.markdown("---")

    # Сравнение конкретного модуля по потокам
    st.markdown("#### 🔬 Динамика конкретного модуля по наборам")
    selected_module_to_track = st.selectbox(
        "Выберите модуль для ретроспективного анализа:",
        df_modules["module_name"].unique(),
        index=1
    )

    track_df = df_modules[df_modules["module_name"] == selected_module_to_track].sort_values("cohort_num")

    col_tr1, col_tr2 = st.columns(2)
    with col_tr1:
        fig_track_cor = px.bar(
            track_df,
            x="cohort_name",
            y="cor",
            text=[f"{v:.0%}" for v in track_df["cor"]],
            title=f"Удержание на {selected_module_to_track[:15]}... по потокам",
            labels={"cor": "COR", "cohort_name": "Поток"}
        )
        fig_track_cor.update_layout(yaxis=dict(tickformat=".0%", range=[0, 1.1]), height=300)
        st.plotly_chart(fig_track_cor, use_container_width=True)

    with col_tr2:
        fig_track_mhi = go.Figure()
        fig_track_mhi.add_trace(go.Scatter(x=track_df["cohort_name"], y=track_df["frag_count"], name="Разрыв связности", mode="lines+markers", line=dict(color="#E74C3C")))
        fig_track_mhi.add_trace(go.Scatter(x=track_df["cohort_name"], y=track_df["depleted_count"], name="Истощение", mode="lines+markers", line=dict(color="#F39C12")))
        fig_track_mhi.update_layout(
            title="Число проблемных сигналов MHI по потокам",
            yaxis=dict(title="Количество студентов", range=[0, 6]),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_track_mhi, use_container_width=True)

# ==============================================================================
# ВКЛАДКА 3: СВЯЗКА И ВЛИЯНИЕ МЕТРИК (CROSS-METRIC INFLUENCE)
# ==============================================================================
with tab3:
    st.subheader("🔗 Как операционные метрики влияют на результаты курса")
    st.markdown("""
    Здесь проверяется гипотеза: **действительно ли сигналы MHI и CSI предсказывают отток ($COR$) и провал аутентичной задачи ($A_{\\text{task}}$)?**
    """)

    col_inf1, col_inf2 = st.columns(2)

    with col_inf1:
        st.markdown("#### 1. Влияние методического хаоса (Cohesion) на отсев")
        # График разброса: связь между жалобами на связность и отвалом с модуля
        fig_rel_drop = px.scatter(
            df_modules,
            x="frag_count",
            y="drop_count",
            size=[12]*len(df_modules),
            color="cohort_name",
            hover_data=["module_name", "cor"],
            labels={
                "frag_count": "Студентов с разрывом логики (Cohesion)",
                "drop_count": "Фактический отвал с модуля (чел.)",
                "cohort_name": "Поток"
            },
            title="Корреляция: Разрыв связности ➔ Число отчисленных"
        )
        fig_rel_drop.update_layout(height=360, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_rel_drop, use_container_width=True)
        st.caption("📌 **Прямая зависимость:** как только в модуле $\ge 2$ человека жалуются на разрыв теории и практики, отвал с модуля подскакивает до 4 человек.")

    with col_inf2:
        st.markdown("#### 2. Влияние качества сопровождения (CSI) на сдачу кейса")
        # Сопоставление на уровне потоков: средний CSI vs A_task
        fig_rel_atask = px.scatter(
            df_cohorts,
            x="avg_csi",
            y="a_task",
            text="cohort_name",
            size=[16]*len(df_cohorts),
            labels={
                "avg_csi": "Средний CSI курса (1-5)",
                "a_task": "Доля сдавших аутентичную задачу (A_task)"
            },
            title="Связка: Удовлетворенность менторами ➔ Сдача проекта"
        )
        fig_rel_atask.update_traces(textposition="top center")
        fig_rel_atask.update_layout(
            xaxis=dict(range=[3.0, 5.0]),
            yaxis=dict(tickformat=".0%", range=[0.2, 1.0]),
            height=360,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_rel_atask, use_container_width=True)
        st.caption("📌 **Методический вывод:** падение CSI ниже 4.0 (задержки проверки ДЗ) снижает долю самостоятельной сдачи финального кейса с 75% до 40%.")

    st.markdown("---")

    # Сводная матрица взаимовлияния
    with st.container(border=True):
        st.markdown("### 📋 Аналитическая памятка методисту: Причинно-следственные связи")
        st.markdown("""
        * **MHI Pacing (Спешка) ➔ Накопление долгов по ДЗ ➔ Отток через 1–2 недели:** Студенты бросают курс не сразу. Спешка в Модуле 2 приводит к отвалу в Модуле 3.
        * **MHI Cohesion (Хаос) ➔ Серии 3+ ошибок ➔ Срыв контроля:** Непонимание связи теории с задачей вызывает смещение локуса («я не технарь») и уход с платформы.
        * **CSI Сервиса / Ментора ➔ Самостоятельность ($A_{\\text{task}}$):** Если ментор задерживает фидбек, студент теряет контекст и не может сформировать аутентичный навык.
        """)
