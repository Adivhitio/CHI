import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Конфигурация страницы Streamlit ---
st.set_page_config(
    page_title="In-Flight Rescue: Оперативный пульс",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. СИНТЕТИЧЕСКАЯ БАЗА ДАННЫХ ОПЕРАТИВНОГО КОНТУРА (КОГОРТА: 14 СТУДЕНТОВ)
# ==============================================================================
@st.cache_data
def load_operational_data():
    # 1.1. Персональные карточки студентов текущего потока на Модуле 2
    # Включает историю MHI с Модуля 1 и 2, число ошибок и дни задержки ДЗ
    students_data = [
        {
            "id": "ST-101", "name": "Алексей Смирнов",
            "m1_pacing": "optimal", "m2_pacing": "rushed",
            "m1_cohesion": "clear", "m2_cohesion": "fragmented",
            "m1_energy": "high", "m2_energy": "moderate",
            "error_loops": 4, "problem_step": "Шаг 2.3 (Рекурсия)",
            "homework_delay_days": 1, "status": "active"
        },
        {
            "id": "ST-102", "name": "Елена Кузнецова",
            "m1_pacing": "rushed", "m2_pacing": "rushed",
            "m1_cohesion": "clear", "m2_cohesion": "clear",
            "m1_energy": "moderate", "m2_energy": "moderate",
            "error_loops": 0, "problem_step": "-",
            "homework_delay_days": 4, "status": "active"
        },
        {
            "id": "ST-103", "name": "Дмитрий Попов",
            "m1_pacing": "optimal", "m2_pacing": "rushed",
            "m1_cohesion": "confused", "m2_cohesion": "fragmented",
            "m1_energy": "moderate", "m2_energy": "depleted",
            "error_loops": 5, "problem_step": "Шаг 2.4 (Бинарный поиск)",
            "homework_delay_days": 6, "status": "active"
        },
        {
            "id": "ST-104", "name": "Анна Соколова",
            "m1_pacing": "optimal", "m2_pacing": "optimal",
            "m1_cohesion": "clear", "m2_cohesion": "clear",
            "m1_energy": "depleted", "m2_energy": "depleted",
            "error_loops": 1, "problem_step": "-",
            "homework_delay_days": 8, "status": "risk_drop"
        },
        {
            "id": "ST-105", "name": "Иван Морозов",
            "m1_pacing": "slow", "m2_pacing": "slow",
            "m1_cohesion": "clear", "m2_cohesion": "clear",
            "m1_energy": "high", "m2_energy": "high",
            "error_loops": 0, "problem_step": "-",
            "homework_delay_days": 0, "status": "active"
        },
        {
            "id": "ST-106", "name": "Мария Федорова",
            "m1_pacing": "rushed", "m2_pacing": "rushed",
            "m1_cohesion": "clear", "m2_cohesion": "fragmented",
            "m1_energy": "moderate", "m2_energy": "depleted",
            "error_loops": 3, "problem_step": "Шаг 2.3 (Рекурсия)",
            "homework_delay_days": 5, "status": "active"
        },
        {
            "id": "ST-107", "name": "Сергей Новиков",
            "m1_pacing": "optimal", "m2_pacing": "optimal",
            "m1_cohesion": "confused", "m2_cohesion": "confused",
            "m1_energy": "high", "m2_energy": "moderate",
            "error_loops": 2, "problem_step": "-",
            "homework_delay_days": 2, "status": "active"
        },
        # Студенты в норме
        {"id": "ST-108", "name": "Ольга Васильева", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "high", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
        {"id": "ST-109", "name": "Павел Ковалев", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "moderate", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
        {"id": "ST-110", "name": "Екатерина Ильина", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "high", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
        {"id": "ST-111", "name": "Михаил Титов", "m1_pacing": "optimal", "m2_pacing": "rushed", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "moderate", "error_loops": 1, "problem_step": "-", "homework_delay_days": 1, "status": "active"},
        {"id": "ST-112", "name": "Наталья Козлова", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "moderate", "m2_energy": "moderate", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
        {"id": "ST-113", "name": "Артем Семенов", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "high", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
        {"id": "ST-114", "name": "Дарья Воробьева", "m1_pacing": "optimal", "m2_pacing": "optimal", "m1_cohesion": "clear", "m2_cohesion": "clear", "m1_energy": "high", "m2_energy": "high", "error_loops": 0, "problem_step": "-", "homework_delay_days": 0, "status": "active"},
    ]
    df_st = pd.DataFrame(students_data)
    return df_st

df_students = load_operational_data()

# ==============================================================================
# 2. РАСЧЕТ ОПЕРАТИВНЫХ АГРЕГАТОВ ДЛЯ ОБРПРОДАКТА
# ==============================================================================
total_cohort = len(df_students)

# Доли аномалий текущего модуля (Модуль 2)
pct_rushed = round((len(df_students[df_students["m2_pacing"] == "rushed"]) / total_cohort) * 100)
pct_fragmented = round((len(df_students[df_students["m2_cohesion"] == "fragmented"]) / total_cohort) * 100)
pct_depleted = round((len(df_students[df_students["m2_energy"] == "depleted"]) / total_cohort) * 100)
pct_backlog = round((len(df_students[df_students["homework_delay_days"] >= 3]) / total_cohort) * 100)
pct_error_loops = round((len(df_students[df_students["error_loops"] >= 3]) / total_cohort) * 100)

# Движок выбора сценария для Обрпродакта
if pct_fragmented >= 20 and pct_error_loops >= 20:
    scenario_id = "SCENARIO_B"
    scenario_title = "Сценарий Б: «Методический тупик» (Разрыв лекций и практики)"
    pitstop_format = "«Aha!-разбор и антипаттерны» (30–45 мин)"
    expert_focus = "Разобрать Шаг 2.3 и 2.4, показать 2 главные типовые ошибки, восстановить ментальную модель задачи."
    chat_draft = """📢 Коллеги, привет!

Видим по пульс-опросу, что практические задания Модуля 2 (особенно рекурсия и поиск) вызвали много трудностей. Это действительно один из самых концептуально сложных шагов курса, споткнуться здесь — абсолютно нормально!

Завтра в 19:00 мск мы проведем короткую Пит-стоп сессию на 35 минут:
• Ведущий эксперт разберет 2 главные ошибки, на которых все споткнулись.
• Покажет правильный ход рассуждений и логику решения.
• Ответит на любые вопросы в прямом эфире.

⏳ Дедлайн по домашнему заданию сдвигаем на +2 дня, чтобы вы спокойно применили разбор. Запись и шпаргалка обязательно будут!"""

elif pct_rushed >= 30 and pct_backlog >= 35:
    scenario_id = "SCENARIO_A"
    scenario_title = "Сценарий А: «Завал объемом» (Перегруз хронометража)"
    pitstop_format = "«Совместный разгон (Live Case Sprint)» (30–45 мин)"
    expert_focus = "Открыть задание ДЗ и в прямом эфире написать первые 40% кода, убрав рутину."
    chat_draft = """📢 Друзья, привет!

Видим, что темп недели оказался слишком плотным и многие не успевают зафиналить практику.

Чтобы снять напряжение, сегодня в 19:30 собираемся на 30-минутный Live Sprint:
• Вместе с экспертом напишем стартовый каркас проекта (первые 40% задачи).
• Разберем лайфхаки, чтобы не тратить часы на рутину.

⏳ Общий дедлайн модуля продлен на 2 дня. Ждем всех!"""

elif pct_depleted >= 25:
    scenario_id = "SCENARIO_C"
    scenario_title = "Сценарий В: «Кризис сил и выгорание»"
    pitstop_format = "«Снятие прессинга и приоритизация» (30 мин)"
    expert_focus = "Разделить ДЗ на 'Обязательное ядро' (на зачет) и 'Факультатив'. Снять прессинг дедлайна."
    chat_draft = """📢 Ребята, внимание!

Пульс-опрос показал, что группа сильно вымоталась на этом модуле. Мы вас слышим: ваша энергия важнее идеальной сдачи в срок.

Что мы делаем прямо сейчас:
1. Выделяем в ДЗ *Обязательное ядро* (для зачета достаточно сдать только его).
2. Остальную часть переводим в статус *Факультативно* (по желанию).
3. Объявляем 3 дня разгрузки без новых тем. Отдышитесь, мы с вами!"""
else:
    scenario_id = "NORMAL"
    scenario_title = "Штатный режим: Аномалий не зафиксировано"
    pitstop_format = "Групповое вмешательство не требуется"
    expert_focus = "Модуль усваивается в нормативном коридоре."
    chat_draft = "Группа движется штатно. Интервенция не требуется."

# ==============================================================================
# 3. БОКОВАЯ ПАНЕЛЬ И СВЕДЕНИЯ О КОГОРТЕ
# ==============================================================================
st.sidebar.title("🎛 Оперативный контекст")
selected_product = st.sidebar.selectbox("Продукт:", ["Data Science (Рескилл B2C)"])
selected_cohort = st.sidebar.selectbox("Поток:", ["Поток 4 (Активный, 14 чел.)"])
selected_module = st.sidebar.selectbox("Анализируемый модуль:", ["Модуль 2: Алгоритмы и структуры данных"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Нормативы оперативного контура:**
* 🔴 **Pacing (Спешка):** порог $> 30\%$
* 🔴 **Cohesion (Хаос):** порог $> 20\%$
* 🔴 **Energy (Истощение):** порог $> 25\%$
* 🔴 **Backlog (Долг $\ge 3$ дн.):** порог $> 35\%$
""")

# ==============================================================================
# 4. ВЕРХНИЙ СВЕТОФОРНЫЙ БАННЕР (ЕСТЬ ЛИ ПРОБЛЕМА?)
# ==============================================================================
st.title("🚨 In-Flight Rescue: Оперативный пульс потока")

# Определение глобального статуса
is_critical = (scenario_id != "NORMAL") or (len(df_students[df_students["homework_delay_days"] >= 6]) >= 2)

if is_critical:
    st.error(f"""
    ### 🔴 ТРЕБУЕТСЯ ВМЕШАТЕЛЬСТВО НА МОДУЛЕ 2!
    * **Где сбой:** 29% группы в методическом тупике (Хаос) | 36% не успевают по темпу | 4 студента требуют адресной помощи.
    * **Что делать:** Обрпродакту — запустить **{pitstop_format}** | Кураторам — отработать 4 карточки в очереди ниже.
    """)
else:
    st.success("### 🟢 ПОТОК ДВИЖЕТСЯ ШТАТНО: Критических аномалий нет, вмешательство не требуется.")

# ==============================================================================
# 5. ДВЕ РОЛЕВЫЕ ВКЛАДКИ
# ==============================================================================
tab_product, tab_curator = st.tabs([
    "👨‍💼 Кабинет Обрпродакта: Групповой сбой и Пит-стоп сессия",
    "🧑‍🏫 Очередь Куратора: Персональный Closed-Loop (4 студента)"
])

# ==============================================================================
# ВКЛАДКА 1: ОБРПРОДАКТ (ГРУППОВОЙ УРОВЕНЬ)
# ==============================================================================
with tab_product:
    st.subheader("1. Где проблема в когорте? (Замер риска)")
    st.caption("Показывает процент активной группы (N=14), попавший под действие негативных факторов.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Спешат (Pacing)", f"{pct_rushed}%", delta="Перегруз" if pct_rushed >= 30 else "Норма", delta_color="inverse")
    c2.metric("Хаос (Cohesion)", f"{pct_fragmented}%", delta="Разрыв логики" if pct_fragmented >= 20 else "Норма", delta_color="inverse")
    c3.metric("Истощены (Energy)", f"{pct_depleted}%", delta="Выгорание" if pct_depleted >= 25 else "Норма", delta_color="inverse")
    c4.metric("Долг ДЗ ≥ 3 дн.", f"{pct_backlog}%", delta="Задержка" if pct_backlog >= 35 else "Норма", delta_color="inverse")
    c5.metric("Петли ≥ 3 ошибок", f"{pct_error_loops}%", delta="Срыв" if pct_error_loops >= 20 else "Норма", delta_color="inverse")

    st.markdown("---")

    st.subheader("2. Что делать обрпродакту? (Готовое управленческое решение)")
    
    with st.container(border=True):
        st.markdown(f"### 🎯 Рекомендуемое действие: **{pitstop_format}**")
        st.markdown(f"**Диагноз учебной среды:** `{scenario_title}`")
        st.info(f"**Фокус ведущего эксперта на эфире:** {expert_focus}")

        st.markdown("#### 💬 Готовый текст анонса для чата группы (скопируйте и отправьте):")
        st.text_area("Текст анонса в Telegram-чат потока:", value=chat_draft, height=230)
        
        btn_col1, btn_col2 = st.columns([1, 4])
        with btn_col1:
            if st.button("✅ Запустить интервенцию", type="primary"):
                st.success("Интервенция запущена: дедлайн сдвинут на +2 дня в LMS, задача на эфир передана эксперту.")
        with btn_col2:
            st.caption("Нажатие автоматически сдвигает системный дедлайн модуля в расписании LMS и отправляет бриф эксперту.")

# ==============================================================================
# ВКЛАДКА 2: КУРАТОР (ПЕРСОНАЛЬНЫЙ CLOSED-LOOP)
# ==============================================================================
with tab_curator:
    st.subheader("📋 Очередь адресного спасения студентов (Приоритет: Высокий)")
    st.caption("Куратор не ищет причины — система выделила студентов с когнитивными и ресурсными сбоями, поставила диагноз и подготовила текст сообщения.")

    # Логика выделения студентов под риском
    flagged_students = []
    for _, s in df_students.iterrows():
        reasons = []
        priority = "🟡 Средний"
        action = ""
        tg_draft = ""

        # Проверка триггеров
        if s["error_loops"] >= 3:
            reasons.append(f"Серия {s['error_loops']} ошибок на {s['problem_step']}")
            priority = "🔴 Критический"
            action = "Снять вину за ошибку, дать наводящую подсказку (Scaffolding)"
            tg_draft = f"Привет, {s['name'].split()[0]}! Заметил, что на {s['problem_step']} возник тупик. Не переживай — это одно из самых коварных мест модуля, здесь спотыкаются почти все. Подсказать логику решения или разобрать ход мысли вместе?"

        if s["m1_pacing"] == "rushed" and s["m2_pacing"] == "rushed":
            reasons.append("Хроническая спешка (2 модуля подряд)")
            action = "Аудит учебного времени, снятие факультативов, мягкий дедлайн"
            tg_draft = f"Привет, {s['name'].split()[0]}! Вижу по пульс-опросу, что тебе уже второй модуль приходится сильно спешить. Давай пересмотрим нагрузку: я помогу выделить обязательный минимум, а второстепенную часть временно отложим, чтобы ты не выгорал(а)."

        if s["m1_energy"] == "depleted" and s["m2_energy"] == "depleted":
            reasons.append("Хроническое истощение (2 модуля подряд)")
            priority = "🔴 Критический"
            action = "Антикризисный созвон: предложить реструктуризацию долгов или академический отпуск"
            tg_draft = f"Привет, {s['name'].split()[0]}! Вижу, что силы совсем на исходе. Твое состояние сейчас важнее любых дедлайнов. Давай созвонимся на 10 минут голосом? Подберем индивидуальный график или оформим небольшую паузу без потери прогресса."

        if s["homework_delay_days"] >= 5 and "Серия" not in " ".join(reasons):
            reasons.append(f"Академический долг: {s['homework_delay_days']} дней")
            action = "Уточнить причину задержки, зафиксировать индивидуальный срок"
            tg_draft = f"Привет, {s['name'].split()[0]}! Вижу, что сдача домашнего задания задерживается на {s['homework_delay_days']} дней. Все ли в порядке? Нужна помощь эксперта или бытовой завал на работе?"

        if reasons:
            flagged_students.append({
                "student": s,
                "priority": priority,
                "reasons": reasons,
                "action": action,
                "tg_draft": tg_draft
            })

    # Сортировка: сначала критические
    flagged_students.sort(key=lambda x: 0 if "🔴" in x["priority"] else 1)

    # Отрисовка карточек студентов
    for item in flagged_students:
        s = item["student"]
        with st.container(border=True):
            head_col1, head_col2, head_col3 = st.columns([2, 1, 1])
            head_col1.markdown(f"### 👤 **{s['name']}** `(ID: {s['id']})`")
            head_col2.markdown(f"**Приоритет:** {item['priority']}")
            head_col3.markdown(f"**Долг ДЗ:** `{s['homework_delay_days']} дн.` | Ошибок: `{s['error_loops']}`")

            st.markdown(f"**Сработавшие триггеры:** {', '.join(item['reasons'])}")
            st.markdown(f"**🎯 Что сделать куратору (SLA 24ч):** {item['action']}")

            with st.expander("💬 Шаблон сообщения в Telegram (нажмите, чтобы скопировать)", expanded=True):
                st.code(item["tg_draft"], language="text")

            act_col1, act_col2 = st.columns([1, 4])
            with act_col1:
                st.button(f"Взять в работу #{s['id']}", key=f"btn_{s['id']}")
            with act_col2:
                st.caption("Фиксирует задачу в CRM со статусом «В работе» и таймером SLA 24 часа.")
