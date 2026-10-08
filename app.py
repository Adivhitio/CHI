import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Конфигурация страницы Streamlit ---
st.set_page_config(
    page_title="LXD & Course Health Monitor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. МОДЕЛЬ ДАННЫХ (КОМПАКТНЫЕ МАТРИЦЫ)
# ==============================================================================
@st.cache_data
def load_audit_data():
    # 1.1. Итоги по наборам (малые когорты по 12-14 человек)
    cohort_cols = ["cohort_num", "cohort_name", "enrolled", "finished", "passed_atask", "r_market", "avg_csi", "avg_sla_hours"]
    cohort_rows = [
        [1, "Поток 1", 12, 8, 6, 0.90, 4.5, 14.0],
        [2, "Поток 2", 14, 7, 4, 0.88, 3.7, 32.0],
        [3, "Поток 3", 13, 6, 4, 0.85, 3.6, 28.0]
    ]
    df_c = pd.DataFrame(cohort_rows, columns=cohort_cols)
    df_c["cr"] = df_c["finished"] / df_c["enrolled"]
    df_c["a_task"] = df_c["passed_atask"] / df_c["finished"]
    df_c["hi_core"] = df_c["cr"] * df_c["a_task"] * df_c["r_market"]
    df_c["hi_label"] = df_c["hi_core"].map(lambda x: f"{x:.3f}")

    # 1.2. Помодульные замеры по наборам (4 модуля)
    mod_cols = [
        "cohort_num", "cohort_name", "module_num", "module_name", 
        "cor", "drop_count", "rushed_count", "frag_count", "depleted_count", 
        "error_loops_3", "mentor_sla", "csi", "lxd_param", "root_cause"
    ]
    mod_rows = [
        # Поток 1
        [1, "Поток 1", 1, "M1: Введение и базовый синтаксис", 1.00, 0, 1, 0, 0, 0, 12, 4.8, "Субъективный контроль", "Легкий вход, ранняя победа в первые 15 минут."],
        [1, "Поток 1", 2, "M2: Алгоритмы и структуры данных", 0.83, 2, 3, 2, 1, 2, 16, 4.2, "Посторонняя нагрузка", "Увеличенный объем практики, умеренное утомление."],
        [1, "Поток 1", 3, "M3: Работа с библиотеками и API", 0.75, 1, 2, 1, 1, 1, 14, 4.4, "Субъективная ценность", "Интересные прикладные задачи, связность сохранена."],
        [1, "Поток 1", 4, "M4: Аутентичный выпускной кейс", 0.67, 1, 2, 1, 2, 2, 15, 4.5, "Субъективный контроль", "Защита самостоятельного проекта."],
        # Поток 2
        [2, "Поток 2", 1, "M1: Введение и базовый синтаксис", 0.93, 1, 1, 0, 0, 1, 14, 4.7, "Трение среды", "Один студент застрял на настройке окружения."],
        [2, "Поток 2", 2, "M2: Алгоритмы и структуры данных", 0.64, 4, 6, 4, 3, 5, 38, 3.3, "Субъективный контроль & Срывы", "Разрыв теории и практики + задержка ревью (38 ч). Серии 3+ ошибок рождают безнадежность."],
        [2, "Поток 2", 3, "M3: Работа с библиотеками и API", 0.57, 1, 4, 2, 3, 3, 30, 3.6, "Посторонняя нагрузка", "Шлейф несданных долгов с Модуля 2; синдром накопленной усталости."],
        [2, "Поток 2", 4, "M4: Аутентичный выпускной кейс", 0.50, 1, 3, 2, 3, 4, 26, 3.8, "Субъективный контроль", "Размытые критерии сдачи кейса; студенты не понимают требований рубрикатора."],
        # Поток 3
        [3, "Поток 3", 1, "M1: Введение и базовый синтаксис", 0.92, 1, 1, 0, 0, 0, 12, 4.6, "Субъективный контроль", "Штатное прохождение вводного модуля."],
        [3, "Поток 3", 2, "M2: Алгоритмы и структуры данных", 0.62, 4, 5, 4, 3, 6, 36, 3.2, "Субъективный контроль & Срывы", "Повторение дефекта: высокая интерактивность формул без scaffolding. Студенты опускают руки на 3-й ошибке."],
        [3, "Поток 3", 3, "M3: Работа с библиотеками и API", 0.54, 1, 4, 3, 4, 3, 24, 3.5, "Посторонняя нагрузка", "Перегрузка теорией без стартовых шаблонов кода; барьер чистого листа."],
        [3, "Поток 3", 4, "M4: Аутентичный выпускной кейс", 0.46, 1, 3, 2, 3, 3, 20, 3.9, "Субъективный контроль", "Падение A_task из-за слабой самостоятельности на предшествующих шагах."]
    ]
    df_m = pd.DataFrame(mod_rows, columns=mod_cols)
    df_m["cor_label"] = df_m["cor"].map(lambda x: f"{x:.0%}")
    return df_c, df_m

df_cohorts, df_modules = load_audit_data()

# ==============================================================================
# 2. САЙДБАР: НАСТРОЙКА ОКНА НАКОПЛЕНИЯ И DATA GATING
# ==============================================================================
st.sidebar.title("🎛 Контур мониторинга")

cohort_window = st.sidebar.slider(
    "Количество анализируемых наборов:",
    min_value=1,
    max_value=3,
    value=3,
    help="Сколько последовательных когорт включено в анализ"
)

filtered_cohorts = df_cohorts[df_cohorts["cohort_num"] <= cohort_window].copy()
total_sample_size = int(filtered_cohorts["enrolled"].sum())
target_sample_size = 30
is_stat_valid = total_sample_size >= target_sample_size

st.sidebar.markdown("---")
st.sidebar.subheader("🛡 Достоверность данных")

if is_stat_valid:
    st.sidebar.success(f"**🔓 Выборка собрана:** N = {total_sample_size} (≥ 30)")
    st.sidebar.caption("Данные сглажены. Тренды и стратегические метрики разблокированы.")
else:
    st.sidebar.warning(f"**🔒 Накопление выборки:** N = {total_sample_size} из {target_sample_size}")
    progress_val = min(1.0, max(0.0, float(total_sample_size) / float(target_sample_size)))
    st.sidebar.progress(progress_val)
    st.sidebar.caption("Малая группа (N < 30). Аналитика скрыта во избежание паники. Доступен оперативный пульс.")

selected_cohort_name = st.sidebar.selectbox(
    "Фокусный поток для анализа в моменте:",
    filtered_cohorts["cohort_name"].tolist(),
    index=len(filtered_cohorts) - 1
)

# ==============================================================================
# 3. ОСНОВНОЙ ЭКРАН
# ==============================================================================
st.title("🎯 Мониторинг качества курса (LXD & Health Audit)")
st.caption("Программа: **Data Science & Аналитика данных** | Подход: Теория эмоций достижения CVT & Теория когнитивной нагрузки CLT")

tab1, tab2, tab3 = st.tabs([
    "⚡ Оперативный пульс (В моменте)",
    "📈 Динамика между наборами (Во времени)",
    "🔗 Связка и влияние метрик (LXD-эффект)"
])

# ==============================================================================
# ВКЛАДКА 1: ОПЕРАТИВНЫЙ ПУЛЬС МОДУЛЯ
# ==============================================================================
with tab1:
    st.subheader(f"📍 Оперативный срез модулей: {selected_cohort_name}")
    cohort_sub = filtered_cohorts[filtered_cohorts["cohort_name"] == selected_cohort_name].iloc[0]
    curr_mod_df = df_modules[df_modules["cohort_name"] == selected_cohort_name].sort_values("module_num").copy()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Студентов в потоке", f"{cohort_sub['enrolled']} чел.")
    k2.metric("Активных на финише", f"{cohort_sub['finished']} из {cohort_sub['enrolled']}")

    total_loops = int(curr_mod_df["error_loops_3"].sum())
    k3.metric("Петли ≥ 3 ошибок", f"{total_loops} инцидентов", delta="Критический срыв" if total_loops > 4 else "В норме", delta_color="inverse")

    max_sla = int(curr_mod_df["mentor_sla"].max())
    k4.metric("Макс. SLA проверки", f"{max_sla} часов", delta="Задержка > 24 ч" if max_sla > 24 else "В норме (< 24 ч)", delta_color="inverse")

    st.markdown("---")

    col_cor, col_signals = st.columns([1, 1])
    with col_cor:
        st.markdown("#### 📉 Карта удержания по модулям (Drop-off Map)")
        fig_cor = px.bar(
            curr_mod_df, x="module_name", y="cor", text="cor_label", color="cor",
            color_continuous_scale="Blues_r", labels={"cor": "Удержание (COR)", "module_name": "Модуль"}
        )
        fig_cor.update_layout(yaxis=dict(range=[0, 1.15], tickformat=".0%"), showlegend=False, height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_cor, use_container_width=True)

    with col_signals:
        st.markdown("#### 🚨 Сигналы MHI и LXD (Абсолютное число голосов)")
        table_view = curr_mod_df[["module_name", "rushed_count", "frag_count", "depleted_count", "error_loops_3", "mentor_sla"]].copy()
        table_view.columns = ["Модуль", "Спешат (чел.)", "Хаос (чел.)", "Истощены (чел.)", "Петли 3+ ошибок", "SLA (ч)"]
        st.dataframe(
            table_view.set_index("Модуль"),
            column_config={
                "Спешат (чел.)": st.column_config.NumberColumn(help="MHI Pacing: ≥ 3 чел. = системный перегруз"),
                "Хаос (чел.)": st.column_config.NumberColumn(help="MHI Cohesion: ≥ 2 чел. = разрыв теории и практики"),
                "Истощены (чел.)": st.column_config.NumberColumn(help="MHI Energy: ≥ 2 чел. = угроза оттока"),
                "Петли 3+ ошибок": st.column_config.NumberColumn(help="Серии безуспешных отправок"),
                "SLA (ч)": st.column_config.NumberColumn(help="Время ожидания проверки ДЗ")
            },
            use_container_width=True
        )
        st.caption("⚠️ **Правило малых групп:** не используем проценты на группе из 12–14 человек. Смотрим на число поднятых рук.")

    with st.container(border=True):
        st.markdown("#### 🛠 Задачи тьютору и кураторам (Closed-Loop оперативного реагирования)")
        crit_mods = curr_mod_df[(curr_mod_df["depleted_count"] >= 2) | (curr_mod_df["error_loops_3"] >= 3)]
        if not crit_mods.empty:
            for _, r in crit_mods.iterrows():
                st.error(
                    f"**{r['module_name']}:** {r['depleted_count']} чел. в истощении, {r['error_loops_3']} петель по 3+ ошибок. "
                    f"**Действие:** персональный контакт со студентами в течение 24 часов (помощь, разбор тупика или дедлайн-каникулы)."
                )
        else:
            st.success("Критических аномалий по MHI и срывам в текущем потоке нет. Все студенты двигаются штатно.")

    st.markdown("---")

    st.markdown("#### 🔬 Глубокая LXD-диагностика модуля")
    chosen_mod = st.selectbox("Выберите модуль для расследования первопричины сбоя:", curr_mod_df["module_name"].tolist(), index=1)
    mod_data = curr_mod_df[curr_mod_df["module_name"] == chosen_mod].iloc[0]

    with st.container(border=True):
        st.markdown(f"### Диагностика: **{mod_data['module_name']}**")
        st.markdown(f"**Ведущий фактор среды:** `{mod_data['lxd_param']}`")
        st.info(f"**Анализ первопричины (Root Cause):** {mod_data['root_cause']}")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Статус по 5 параметрам модели LXD:**")
            p1_stat = "🔴 Перегруз" if mod_data["rushed_count"] >= 3 else "🟢 Норма"
            p2_stat = "🔴 Задержка" if mod_data["mentor_sla"] > 24 else "🟢 Норма"
            p3_stat = "🔴 Разрушен" if mod_data["frag_count"] >= 2 else "🟢 Устойчив"
            p5_stat = "🔴 Критический срыв" if mod_data["error_loops_3"] >= 3 else "🟢 Стабильно"

            st.markdown(f"""
            * **Посторонняя нагрузка:** {p1_stat} ({mod_data['rushed_count']} жалоб на спешку)
            * **Трение среды:** {p2_stat} (SLA ревью = {mod_data['mentor_sla']} ч)
            * **Субъективный контроль:** {p3_stat} ({mod_data['frag_count']} чел. не поняли связи)
            * **Субъективная ценность:** CSI модуля = `{mod_data['csi']}` / 5.0
            * **Эмоциональная динамика:** {p5_stat} ({mod_data['error_loops_3']} тупиковых петель)
            """)
        with col_d2:
            st.markdown("**Рекомендуемые микро-интервенции (чек-лист LXD):**")
            st.markdown("""
            * [ ] **Критерий №19 (Scaffolding):** Внедрить автоматическую контекстную подсказку на 2-й ошибке подряд.
            * [ ] **Критерий №28 (Безопасность проб):** Заменить резкие экраны ошибки на нейтральный диагностический фидбек.
            * [ ] **Критерий №16 (Критерии приемки):** Опубликовать открытый чек-лист самопроверки перед сдачей ДЗ.
            * [ ] **Критерий №4 (Справочники «с полки»):** Вынести синтаксис формул в выпадающую подсказку рядом с полем ввода.
            """)

# ==============================================================================
# ВКЛАДКА 2: ДИНАМИКА ВО ВРЕМЕНИ
# ==============================================================================
with tab2:
    st.subheader("📈 Динамика показателей качества между наборами")

    if not is_stat_valid:
        st.warning("### 🔒 Аналитика трендов заблокирована (Идет накопление выборки)")
        st.markdown(f"""
        Для защиты от статистического шума на малых когортах расчет трендов активируется **только при выборке N ≥ 30 студентов (окно из 3 наборов)**.

        * **Текущий статус:** собрано **{total_sample_size}** из **{target_sample_size}** профилей (потоков в анализе: {cohort_window}).
        * **Почему это необходимо:** при малой выборке уход одного заболевшего студента искажает показатели на 8–10%, создавая ложную панику.
        * **Что делать сейчас:** используйте **Вкладку 1** для оперативной помощи студентам текущего потока.
        """)
        progress_val_tab2 = min(1.0, max(0.0, float(total_sample_size) / float(target_sample_size)))
        st.progress(progress_val_tab2)
    else:
        st.success(f"🔓 **Выборка валидна (N = {total_sample_size} по 3 потокам).** Случайный шум сглажен. Данные готовы к методическим выводам.")

        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.markdown("#### 🎯 Динамика методического ядра здоровья (HI_core)")
            fig_hi = px.line(filtered_cohorts, x="cohort_name", y="hi_core", text="hi_label", markers=True, labels={"hi_core": "HI_core", "cohort_name": "Поток"})
            fig_hi.add_hrect(y0=0.50, y1=1.00, fillcolor="rgba(46, 204, 113, 0.1)", line_width=0, annotation_text="Здоровая зона (≥ 0.50)")
            fig_hi.add_hrect(y0=0.25, y1=0.50, fillcolor="rgba(241, 196, 15, 0.1)", line_width=0, annotation_text="Зона риска")
            fig_hi.add_hrect(y0=0.00, y1=0.25, fillcolor="rgba(231, 76, 60, 0.1)", line_width=0, annotation_text="Критическая зона")
            fig_hi.update_traces(textposition="top center", line=dict(color="#2C3E50", width=3))
            fig_hi.update_layout(yaxis_range=[0, 0.7], height=360, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_hi, use_container_width=True)

        with col_t2:
            st.markdown("#### 🔍 Разложение: Доходимость (CR) vs Сдача кейса (A_task)")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=filtered_cohorts["cohort_name"], y=filtered_cohorts["cr"], name="CR (Доходимость)", marker_color="#3498DB"))
            fig_bar.add_trace(go.Bar(x=filtered_cohorts["cohort_name"], y=filtered_cohorts["a_task"], name="A_task (Сдача кейса)", marker_color="#2ECC71"))
            fig_bar.update_layout(
                barmode="group", yaxis=dict(tickformat=".0%", range=[0, 1.05]), height=360,
                margin=dict(t=20, b=20, l=20, r=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🔁 Ретроспектива модулей: Повторяемость дефекта по наборам")
        selected_mod_track = st.selectbox("Выберите модуль для проверки повторяемости сбоев:", df_modules["module_name"].unique(), index=1)
        mod_track_df = df_modules[df_modules["module_name"] == selected_mod_track].sort_values("cohort_num").copy()

        c_tr1, c_tr2 = st.columns(2)
        with c_tr1:
            fig_track_cor = px.bar(mod_track_df, x="cohort_name", y="cor", text="cor_label", title=f"Удержание (COR) на {selected_mod_track[:20]}...", labels={"cor": "COR", "cohort_name": "Поток"})
            fig_track_cor.update_layout(yaxis=dict(tickformat=".0%", range=[0, 1.1]), height=300)
            st.plotly_chart(fig_track_cor, use_container_width=True)

        with c_tr2:
            fig_track_mhi = go.Figure()
            fig_track_mhi.add_trace(go.Scatter(x=mod_track_df["cohort_name"], y=mod_track_df["frag_count"], name="Разрыв связности", mode="lines+markers", line=dict(color="#E74C3C")))
            fig_track_mhi.add_trace(go.Scatter(x=mod_track_df["cohort_name"], y=mod_track_df["error_loops_3"], name="Петли 3+ ошибок", mode="lines+markers", line=dict(color="#8E44AD")))
            fig_track_mhi.update_layout(
                title="Число критических сигналов по наборам", yaxis=dict(title="Количество студентов / инцидентов", range=[0, 8]),
                height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_track_mhi, use_container_width=True)

        latest_rec = mod_track_df.iloc[-1]
        prev_rec = mod_track_df.iloc[-2] if len(mod_track_df) > 1 else latest_rec
        if latest_rec["frag_count"] >= 2 and prev_rec["frag_count"] >= 2:
            st.error(f"🚨 **Подтвержден системный дефект:** Модуль «{selected_mod_track}» дает сбой 2 потока подряд. Необходим редизайн по чек-листу LXD.")
        else:
            st.success(f"✅ На модуле «{selected_mod_track}» нет устойчивого системного сбоя между наборами.")

# ==============================================================================
# ВКЛАДКА 3: СВЯЗКА И ВЛИЯНИЕ МЕТРИК
# ==============================================================================
with tab3:
    st.subheader("🔗 Взаимосвязь метрик: Как опережающие сигналы бьют по результату")

    if not is_stat_valid:
        st.warning("### 🔒 Анализ связок заблокирован (Недостаточно данных)")
        st.markdown(f"Для выявления корреляций требуется минимум **30 студентов ({target_sample_size})**. Увеличьте ползунок наборов в боковой панели до **3**.")
    else:
        st.markdown("Проверяем методическую гипотезу: **ведут ли субъективный хаос и сервисные задержки к оттоку (COR) и провалу кейса (A_task)?**")

        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.markdown("#### 1. Связка: Методический хаос ➔ Отвал с модуля")
            fig_rel1 = px.scatter(
                df_modules, x="frag_count", y="drop_count", color="cohort_name", hover_data=["module_name", "cor"],
                labels={"frag_count": "Жалоб на разрыв связности (чел.)", "drop_count": "Фактический отвал с модуля (чел.)", "cohort_name": "Поток"},
                title="Разрыв теории и практики ➔ Падение удержания"
            )
            fig_rel1.update_traces(marker=dict(size=14))
            fig_rel1.update_layout(height=360, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_rel1, use_container_width=True)
            st.caption("📌 **Прямой эффект:** при ≥ 3 жалобах на разрыв теории с практикой отвал возрастает до 4 человек.")

        with col_inf2:
            st.markdown("#### 2. Связка: Задержка фидбека (SLA) ➔ Сдача кейса")
            fig_rel2 = px.scatter(
                filtered_cohorts, x="avg_sla_hours", y="a_task", text="cohort_name",
                labels={"avg_sla_hours": "Средний SLA проверки ДЗ ментором (часов)", "a_task": "Доля сдавших задачу (A_task)"},
                title="Задержка обратной связи ➔ Обвал навыка"
            )
            fig_rel2.update_traces(textposition="top center", marker=dict(size=16))
            fig_rel2.update_layout(xaxis=dict(range=[10, 45]), yaxis=dict(tickformat=".0%", range=[0.2, 1.0]), height=360, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_rel2, use_container_width=True)
            st.caption("📌 **Прямой эффект:** когда проверка ДЗ длится дольше 24 ч, студент теряет импульс, а сдача проекта падает с 75% до 40%.")

        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 📋 Резюме для продуктовой и методической команды:")
            st.markdown("""
            1. **MHI Pacing (Спешка) ➔ Академический долг ➔ Отток через 2 недели:** Студент бросает курс не в момент спешки, а накопив несданные дедлайны к следующему модулю.
            2. **MHI Cohesion (Хаос) ➔ Петли 3+ ошибок ➔ Срыв контроля:** Непонимание логики задания толкает студента на серию ошибок; смещение атрибуции на «я не технарь» ведет к закрытию платформы.
            3. **Feedback SLA (> 24 ч) ➔ «Иллюзия доходимости»:** Длительное ожидание ответа провоцирует формальный проклик материалов без глубокого усвоения навыка.
            """)
