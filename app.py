import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Конфигурация страницы Streamlit ---
st.set_page_config(
    page_title="LXD & Course Health Monitor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. МОДЕЛЬ ДАННЫХ: 2 РЕСКИЛЛ-ПРОДУКТА (КРУПНЫЕ И МАЛЫЕ КОГОРТЫ)
# ==============================================================================
@st.cache_data
def load_audit_data():
    # 1.1. Реестр Валидных срезов (N >= 30) для стратегического аудита
    slice_cols = [
        "product", "slice_id", "slice_name", "cohorts_included", 
        "enrolled", "finished", "passed_atask", "r_market"
    ]
    slice_rows = [
        # Продукт 1: Крупные когорты (каждый поток N=40..45 сразу формирует срез)
        ["Data Science (Крупные когорты)", "DS_S1", "Срез 1 [Поток 1]", "Поток 1", 45, 28, 24, 0.90],
        ["Data Science (Крупные когорты)", "DS_S2", "Срез 2 [Поток 2]", "Поток 2", 42, 27, 24, 0.92],
        
        # Продукт 2: Малые когорты (10..15 чел., срез накопился за Потоки 1-3)
        ["Веб-разработка (Малые когорты)", "WEB_S1", "Срез 1 [Потоки 1–3]", "Потоки 1, 2, 3", 39, 21, 14, 0.86]
    ]
    df_slices = pd.DataFrame(slice_rows, columns=slice_cols)
    df_slices["cr"] = df_slices["finished"] / df_slices["enrolled"]
    df_slices["a_task"] = df_slices["passed_atask"] / df_slices["finished"]
    df_slices["hi_core"] = df_slices["cr"] * df_slices["a_task"] * df_slices["r_market"]
    df_slices["output"] = df_slices["cr"] * df_slices["a_task"]
    
    def calc_status(hi):
        if hi >= 0.50:
            return "🟢 Здоровый"
        elif hi >= 0.25:
            return "🟡 Зона риска"
        return "🔴 Критический"
    df_slices["status"] = df_slices["hi_core"].map(calc_status)

    # 1.2. Реестр потоков в процессе (In-Flight cohorts) для оперативного контура
    inflight_cols = ["product", "cohort_name", "enrolled", "finished", "status_desc"]
    inflight_rows = [
        ["Data Science (Крупные когорты)", "Поток 2 (Текущий)", 42, 27, "Поток завершен, сформировал Срез 2 (N=42)"],
        ["Веб-разработка (Малые когорты)", "Поток 4 (В процессе)", 12, 7, "Идет накопление выборки в Срез 2 (12 из 30 чел.)"]
    ]
    df_inflight = pd.DataFrame(inflight_rows, columns=inflight_cols)

    # 1.3. Помодульная телеметрия для текущих потоков (4 модуля)
    mod_cols = [
        "product", "cohort_name", "module_num", "module_name",
        "cor", "drop_count", "rushed_count", "frag_count", "depleted_count",
        "error_loops_3", "mentor_sla", "csi", "lxd_factor", "root_cause_analysis"
    ]
    mod_rows = [
        # Data Science (Поток 2 - крупная группа)
        ["Data Science (Крупные когорты)", "Поток 2 (Текущий)", 1, "M1: Введение и базовый Python", 0.95, 2, 3, 1, 1, 1, 14, 4.8, "Субъективный контроль", "Штатный старт, ранняя победа в первые 15 минут."],
        ["Data Science (Крупные когорты)", "Поток 2 (Текущий)", 2, "M2: Высшая математика и Линал", 0.78, 7, 12, 6, 5, 8, 22, 3.8, "Посторонняя нагрузка", "Высокая плотность формул, дефицит пошаговых примеров."],
        ["Data Science (Крупные когорты)", "Поток 2 (Текущий)", 3, "M3: Машинное обучение (ML)", 0.69, 4, 8, 4, 5, 5, 18, 4.2, "Субъективный контроль", "Умеренная сложность, практика поддержана шаблонами."],
        ["Data Science (Крупные когорты)", "Поток 2 (Текущий)", 4, "M4: Аутентичный дипломный кейс", 0.64, 2, 5, 3, 4, 3, 16, 4.5, "Субъективная ценность", "Высокая мотивация решения боевого индустриального кейса."],

        # Веб-разработка (Поток 4 - малая группа, 12 человек)
        ["Веб-разработка (Малые когорты)", "Поток 4 (В процессе)", 1, "M1: HTML/CSS и Семантика", 1.00, 0, 1, 0, 0, 0, 12, 4.8, "Субъективный контроль", "Низкий входной барьер, все студенты в графике."],
        ["Веб-разработка (Малые когорты)", "Поток 4 (В процессе)", 2, "M2: JavaScript: Асинхронность и DOM", 0.67, 4, 5, 4, 3, 5, 38, 3.2, "Субъективный контроль & Срывы", "Разрыв между лекциями и практикой + задержка код-ревью ментором (38 ч). Серии 3+ ошибок рождают безнадежность."],
        ["Веб-разработка (Малые когорты)", "Поток 4 (В процессе)", 3, "M3: Архитектура React и API", 0.58, 1, 4, 2, 3, 3, 26, 3.6, "Посторонняя нагрузка", "Шлейф несданных долгов с Модуля 2; синдром накопленной усталости."],
        ["Веб-разработка (Малые когорты)", "Поток 4 (В процессе)", 4, "M4: Финальный аутентичный проект", 0.58, 0, 2, 2, 2, 2, 18, 4.0, "Субъективный контроль", "Сложности с самостоятельной декомпозицией ТЗ без подсказок."]
    ]
    df_modules = pd.DataFrame(mod_rows, columns=mod_cols)
    df_modules["cor_label"] = df_modules["cor"].map(lambda x: f"{x:.0%}")
    return df_slices, df_inflight, df_modules

df_slices, df_inflight, df_modules = load_audit_data()

# ==============================================================================
# 2. САЙДБАР: ВЫБОР ПРОДУКТА И СПРАВОЧНИК МЕТРИК
# ==============================================================================
st.sidebar.title("🎛 Навигация аудита")

available_products = df_slices["product"].unique().tolist()
selected_product = st.sidebar.selectbox("Выберите продукт для анализа:", available_products)

# Фильтрация данных под выбранный продукт
prod_slices = df_slices[df_slices["product"] == selected_product].copy()
prod_inflight = df_inflight[df_inflight["product"] == selected_product].iloc[0]
prod_modules = df_modules[df_modules["product"] == selected_product].copy()

# Статус накопления данных
st.sidebar.markdown("---")
st.sidebar.subheader("🛡 Статус выборки продукта")
if "Крупные" in selected_product:
    st.sidebar.success("🟢 **Крупные когорты (N ≥ 40):**\nКаждый запуск формирует валидный срез. Стратегический аудит доступен сразу по каждому набору.")
else:
    st.sidebar.warning(f"🟡 **Малые когорты (10–15 чел.):**\n{prod_inflight['status_desc']}")
    st.sidebar.caption("Стратегический аудит курса рассчитывается только по объединенному Срезу 1 (N=39). В текущем Потоке 4 активен только оперативный пульс.")

# Развернутый справочник / легенда
with st.sidebar.expander("📖 Легенда и глоссарий метрик", expanded=False):
    st.markdown("""
    **Ядро здоровья ($HI_{\\text{core}}$):**
    * Формула: $CR \\times A_{\\text{task}} \\times R_{\\text{market}}$
    * Смысл: реальная доля от всех купивших курс, кто освоил актуальный для рынка навык.
    * Пороги: 🟢 $\ge 0.500$ (Здоровый) | 🟡 $0.250–0.499$ (Зона риска) | 🔴 $< 0.250$ (Критический).

    **Валидный срез (Audit Slice):**
    * Объединенный пул студентов ($N \\ge 30$), очищающий метрики от случайного шума малых групп (болезни, авралы).

    **MHI (Module Health Index):**
    * *Pacing (Ритм):* перегруз объемом или хронометражем (порог: $\ge 3$ чел. спешат).
    * *Cohesion (Связность):* методический разрыв лекций и практики (порог: $\ge 2$ чел. в хаосе).
    * *Energy (Ресурс):* выгорание и риск тихого оттока (порог: $\ge 2$ чел. в истощении).

    **Feedback SLA:**
    * Время проверки ДЗ ментором. Задержка $> 24$ ч гасит учебный импульс взрослого студента.
    """)

# ==============================================================================
# 3. ОСНОВНОЙ ЭКРАН ДАШБОРДА
# ==============================================================================
st.title("🎓 Система аудита образовательных продуктов (LXD & Health Monitor)")
st.caption(f"Продукт: **{selected_product}** | Методологический фреймворк: CVT (Эмоции достижения) & CLT (Когнитивная нагрузка)")

tab1, tab2, tab3 = st.tabs([
    "⚡ Вкладка 1: Оперативный пульс (Продакт + Сопровождение)",
    "🎯 Вкладка 2: Аудит качества курса (Продакт + Продюсер + Методолог)",
    "🔬 Вкладка 3: Аналитика и гипотезы (Методологи + Аналитики)"
])

# ==============================================================================
# ВКЛАДКА 1: ОПЕРАТИВНЫЙ ПУЛЬС (ТЕКУЩИЙ ПОТОК IN-FLIGHT)
# ==============================================================================
with tab1:
    st.subheader(f"📍 Оперативное состояние: {prod_inflight['cohort_name']}")
    st.caption("Фокус: спасение студентов текущей группы в реальном времени. Здесь нет процентов $HI$ — только абсолютные сигналы и задачи сопровождения.")

    # Верхние KPI карточки текущего потока в абсолютных значениях
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Зачислено на поток", f"{prod_inflight['enrolled']} чел.")
    k2.metric("Активных студентов", f"{prod_inflight['finished']} из {prod_inflight['enrolled']}")
    
    total_loops = int(prod_modules["error_loops_3"].sum())
    k3.metric(
        "Петли ≥ 3 ошибок (Срыв контроля)", 
        f"{total_loops} инцидентов", 
        delta="Критический срыв CVT" if total_loops > 4 else "В норме", 
        delta_color="inverse"
    )

    max_sla = int(prod_modules["mentor_sla"].max())
    k4.metric(
        "Макс. SLA проверки ревью", 
        f"{max_sla} часов", 
        delta="Задержка > 24 ч" if max_sla > 24 else "В норме (< 24 ч)", 
        delta_color="inverse"
    )

    st.markdown("---")

    col_cor, col_signals = st.columns([1, 1])

    with col_cor:
        st.markdown("#### 📉 Воронка удержания потока (Drop-off Map)")
        fig_cor = px.bar(
            prod_modules, x="module_name", y="cor", text="cor_label", color="cor",
            color_continuous_scale="Blues_r", labels={"cor": "Удержание (COR)", "module_name": "Модуль"}
        )
        fig_cor.update_layout(yaxis=dict(range=[0, 1.15], tickformat=".0%"), showlegend=False, height=330, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_cor, use_container_width=True)

    with col_signals:
        st.markdown("#### 🚨 Сигналы MHI и телеметрия платформы (в абсолютных числах)")
        table_view = prod_modules[["module_name", "rushed_count", "frag_count", "depleted_count", "error_loops_3", "mentor_sla"]].copy()
        table_view.columns = ["Модуль", "Спешат (чел.)", "Хаос (чел.)", "Истощены (чел.)", "Петли 3+ ошибок", "SLA (ч)"]
        st.dataframe(
            table_view.set_index("Модуль"),
            column_config={
                "Спешат (чел.)": st.column_config.NumberColumn(help="MHI Pacing: перегруз объемом"),
                "Хаос (чел.)": st.column_config.NumberColumn(help="MHI Cohesion: разрыв связки теории и ДЗ"),
                "Истощены (чел.)": st.column_config.NumberColumn(help="MHI Energy: угроза тихого оттока"),
                "Петли 3+ ошибок": st.column_config.NumberColumn(help="Серии неудачных попыток сдачи подряд"),
                "SLA (ч)": st.column_config.NumberColumn(help="Время ожидания проверки ДЗ ментором")
            },
            use_container_width=True
        )

    # Список задач для службы сопровождения (Closed-Loop)
    with st.container(border=True):
        st.markdown("#### 🛠 Задачи службы сопровождения (Closed-Loop реагирования)")
        crit_mods = prod_modules[(prod_modules["depleted_count"] >= 2) | (prod_modules["error_loops_3"] >= 3)]
        if not crit_mods.empty:
            for _, r in crit_mods.iterrows():
                st.error(
                    f"**{r['module_name']}:** {r['depleted_count']} чел. в истощении, {r['error_loops_3']} петель по 3+ ошибок. "
                    f"**Действие тьютору:** персональный контакт в течение 24 часов (предложить подсказку, разобрать тупик или дать индивидуальный дедлайн)."
                )
        else:
            st.success("Критических инцидентов по MHI и тупиковым ошибкам в текущем потоке нет. Группа движется стабильно.")

# ==============================================================================
# ВКЛАДКА 2: АУДИТ КАЧЕСТВА КУРСА (СТРОГО НА ВАЛИДНЫХ СРЕЗАХ N >= 30)
# ==============================================================================
with tab2:
    st.subheader("🎯 Стратегический аудит программы (Валидные срезы)")
    st.caption("Данные очищены от случайного шума малых групп ($N \\ge 30$). Позволяет оценить реальное здоровье курса и архитектурные дефекты среды.")

    selected_slice_name = st.selectbox(
        "Выберите Валидный срез для аудита:",
        prod_slices["slice_name"].tolist()
    )
    slice_data = prod_slices[prod_slices["slice_name"] == selected_slice_name].iloc[0]

    # Верхние карточки здоровья среза
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Методическое ядро (HI_core)", f"{slice_data['hi_core']:.3f}", slice_data["status"])
    s2.metric("Доходимость среза (CR)", f"{slice_data['cr']:.1%}", f"{slice_data['finished']} из {slice_data['enrolled']} чел.")
    s3.metric("Сдача задачи (A_task)", f"{slice_data['a_task']:.1%}", f"{slice_data['passed_atask']} из {slice_data['finished']} чел.")
    s4.metric("Актуальность стека (R_market)", f"{slice_data['r_market']:.2f}", "Рейтинг рынка труда")

    st.markdown("---")

    col_chart_s1, col_chart_s2 = st.columns([1, 1])

    with col_chart_s1:
        st.markdown(f"#### 📊 Декомпозиция ядра здоровья ({selected_slice_name})")
        decomp_fig = go.Figure()
        decomp_fig.add_trace(go.Bar(x=["Доходимость (CR)", "Сдача кейса (A_task)", "Актуальность (R_market)"],
                                    y=[slice_data["cr"], slice_data["a_task"], slice_data["r_market"]],
                                    marker_color=["#3498DB", "#2ECC71", "#E67E22"]))
        decomp_fig.add_hline(y=0.60, line_dash="dot", line_color="red", annotation_text="Минимальный порог качества (60%)")
        decomp_fig.update_layout(yaxis=dict(range=[0, 1.1], tickformat=".0%"), height=330, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(decomp_fig, use_container_width=True)

    with col_chart_s2:
        st.markdown("#### 🗺 Карта потерь на модулях (Drop-off Map среза)")
        fig_sl_mod = px.bar(
            prod_modules, x="module_name", y="cor", text="cor_label", color="cor",
            color_continuous_scale="Blues_r", labels={"cor": "Удержание (COR)", "module_name": "Модуль"}
        )
        fig_sl_mod.update_layout(yaxis=dict(range=[0, 1.15], tickformat=".0%"), showlegend=False, height=330, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_sl_mod, use_container_width=True)

    # Верхнеуровневый диагноз по 5 аспектам модели LXD
    with st.container(border=True):
        st.markdown("### 🏛 Архитектурный аудит образовательной среды (LXD Diagnosis)")
        st.markdown(f"**Анализируемый срез:** `{slice_data['slice_name']}` (Включены: {slice_data['cohorts_included']}, выборка: **{slice_data['enrolled']} студентов**)")
        
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            st.markdown("#### 🔍 Выявленные сбои характеристик среды:")
            if "Малые" in selected_product:
                st.markdown("""
                * **Субъективный контроль (Критический сбой):** на Модуле 2 студенты массово теряют понимание связи лекций с практикой. Размытые критерии сдачи и задержка проверки (38 ч) обнуляют оценку контроля.
                * **Эмоциональная динамика (Порог оттока):** фиксация $\ge 5$ тупиковых петель ошибок на модуль смещает атрибуцию неудачи («я не технарь»), запуская уход с курса.
                * **Посторонняя нагрузка:** дефицит промежуточных шаблонов перегружает рабочую память второстепенными деталями.
                """)
            else:
                st.markdown("""
                * **Посторонняя когнитивная нагрузка (Зона риска):** резкий скачок плотности формул на Модуле 2 вызывает перегруз хронометража (12 жалоб на спешку).
                * **Субъективный контроль:** в норме, но требует внимания на стыке математики и алгоритмов.
                * **Субъективная ценность:** высокая — аутентичный проект высоко оценивается рынком ($R_{\\text{market}} = 0.92$).
                """)

        with diag_col2:
            st.markdown("#### 🛠 Фокусы доработки среды (Рекомендации методистам):")
            st.markdown("""
            1. **Архитектура поддержки и критериев (Scaffolding / Контроль):**
               * Спроектировать систему адаптивной поддержки в точках затруднений и обеспечить прозрачность критериев приемки до начала решения.
            2. **Структура и хронометраж контента (Когнитивная нагрузка):**
               * Декомпозировать неделимые блоки практики на 15–20-минутные кванты и устранить избыточный теоретический контекст.
            3. **Процедурная среда и доступность (Трение среды):**
               * Устранить технические барьеры софта и сократить норматив код-ревью менторами до $< 24$ часов.
            4. **Безопасность проб (Эмоциональная динамика):**
               * Спроектировать механизм разрыва тупиковых циклов ошибок без наказания или стыдящей коммуникации.
            """)

# ==============================================================================
# ВКЛАДКА 3: АНАЛИТИКА И ГИПОТЕЗЫ (МЕТОДОЛОГИ + АНАЛИТИКИ)
# ==============================================================================
with tab3:
    st.subheader("🔬 Аналитическое пространство: Проверка гипотез и взаимосвязей")
    st.caption("Фокус: доказательная база для методического совета. Сопоставление срезов «До/После» и проверка влияния опережающих сигналов на результат.")

    # Блок 1. Сравнение срезов (если срезов >= 2)
    st.markdown("#### 1. Динамика качества между Валидными срезами")
    if len(prod_slices) >= 2:
        fig_slices_comp = px.bar(
            prod_slices, x="slice_name", y=["cr", "a_task", "hi_core"],
            barmode="group",
            labels={"value": "Значение", "variable": "Метрика", "slice_name": "Валидный срез"},
            color_discrete_map={"cr": "#3498DB", "a_task": "#2ECC71", "hi_core": "#2C3E50"}
        )
        fig_slices_comp.update_layout(yaxis=dict(tickformat=".0%", range=[0, 1.1]), height=340)
        st.plotly_chart(fig_slices_comp, use_container_width=True)
        st.caption("✅ **Вывод:** редизайн Модуля 2 в Потоке 2 позволил поднять $HI_{\\text{core}}$ с 0.480 до 0.526, переведя курс в зеленую зону.")
    else:
        st.info("Для данного продукта сформирован 1 Валидный срез. Сравнение «До/После» активируется после завершения накопления Среза 2.")

    st.markdown("---")

    # Блок 2. Взаимосвязь метрик: Как опережающие сигналы бьют по результату
    st.markdown("#### 2. Доказательная база: Взаимосвязь опережающих сигналов и результата")
    
    col_rel1, col_rel2 = st.columns(2)

    with col_rel1:
        st.markdown("##### Связка 1: Методический хаос (Cohesion) ➔ Отвал с модуля")
        fig_r1 = px.scatter(
            prod_modules, x="frag_count", y="drop_count", color="module_name",
            labels={"frag_count": "Жалоб на разрыв связности (чел.)", "drop_count": "Отвал с модуля (чел.)"}
        )
        fig_r1.update_traces(marker=dict(size=14))
        fig_r1.update_layout(height=320, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_r1, use_container_width=True)
        st.caption("📌 **Паттерн:** рост непонимания связки теории и практики свыше 3 человек приводит к отчислению 4–7 студентов.")

    with col_rel2:
        st.markdown("##### Связка 2: Задержка ревью (SLA) ➔ Срыв контроля")
        fig_r2 = px.scatter(
            prod_modules, x="mentor_sla", y="error_loops_3", color="module_name",
            labels={"mentor_sla": "SLA проверки ДЗ ментором (часов)", "error_loops_3": "Петли ≥ 3 ошибок (инцидентов)"}
        )
        fig_r2.update_traces(marker=dict(size=14))
        fig_r2.update_layout(height=320, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_r2, use_container_width=True)
        st.caption("📌 **Паттерн:** при проверке ДЗ дольше 24 часов студенты теряют контекст, число тупиковых ошибок возрастает в 3 раза.")

    with st.container(border=True):
        st.markdown("#### 📋 Аналитическое резюме для Методического совета:")
        st.markdown("""
        * **MHI Pacing (Спешка) ➔ Накопление долгов по ДЗ:** студенты не бросают курс сразу; перегруз на Модуле 2 приводит к отвалу на Модуле 3.
        * **MHI Cohesion (Хаос) ➔ Тупиковые петли ➔ Потеря контроля:** непонимание смысла задания заставляет совершать серии ошибок, что ведет к срыву в безнадежность.
        * **SLA проверки (> 24 ч) ➔ Обвал $A_{\\text{task}}$:** длительное ожидание ментора разрушает учебную автономность, снижая самостоятельность сдачи итогового кейса.
        """)
