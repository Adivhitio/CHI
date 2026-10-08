import streamlit as st
import pandas as pd
import numpy as np
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
# 1. МОДЕЛЬ ДАННЫХ КУРСА (1 КУРС × 3 ПОТОКА ПО 12-14 ЧЕЛОВЕК)
# ==============================================================================
@st.cache_data
def load_audit_data():
    # 1.1. Когортные итоги потоков (малые когорты)
    cohorts_raw = [
        {
            "cohort_num": 1,
            "cohort_name": "Поток 1",
            "enrolled": 12,
            "finished": 8,
            "passed_atask": 6,
            "r_market": 0.90,
            "avg_csi": 4.5,
            "avg_sla_hours": 14.0
        },
        {
            "cohort_num": 2,
            "cohort_name": "Поток 2",
            "enrolled": 14,
            "finished": 7,
            "passed_atask": 4,
            "r_market": 0.88,
            "avg_csi": 3.7,
            "avg_sla_hours": 32.0
        },
        {
            "cohort_num": 3,
            "cohort_name": "Поток 3",
            "enrolled": 13,
            "finished": 6,
            "passed_atask": 4,
            "r_market": 0.85,
            "avg_csi": 3.6,
            "avg_sla_hours": 28.0
        }
    ]
    df_c = pd.DataFrame(cohorts_raw)
    df_c["cr"] = df_c["finished"] / df_c["enrolled"]
    df_c["a_task"] = df_c["passed_atask"] / df_c["finished"]
    df_c["hi_core"] = df_c["cr"] * df_c["a_task"] * df_c["r_market"]

    # 1.2. Помодульные замеры по потокам (4 модуля)
    modules_raw = [
        # --- ПОТОК 1 ---
        {
            "cohort_num": 1,
            "cohort_name": "Поток 1",
            "module_num": 1,
            "module_name": "M1: Введение и базовый синтаксис",
            "cor": 1.00,
            "drop_count": 0,
            "rushed_count": 1,
            "frag_count": 0,
            "depleted_count": 0,
            "error_loops_3": 0,
            "mentor_sla": 12,
            "csi": 4.8,
            "lxd_param": "Субъективный контроль",
            "root_cause": "Легкий вход, ранняя победа в первые 15 минут."
        },
        {
            "cohort_num": 1,
            "cohort_name": "Поток 1",
            "module_num": 2,
            "module_name": "M2: Алгоритмы и структуры данных",
            "cor": 0.83,
            "drop_count": 2,
            "rushed_count": 3,
            "frag_count": 2,
            "depleted_count": 1,
            "error_loops_3": 2,
            "mentor_sla": 16,
            "csi": 4.2,
            "lxd_param": "Посторонняя нагрузка",
            "root_cause": "Увеличенный объем практики, умеренное утомление."
        },
        {
            "cohort_num": 1,
            "cohort_name": "Поток 1",
            "module_num": 3,
            "module_name": "M3: Работа с библиотеками и API",
            "cor": 0.75,
            "drop_count": 1,
            "rushed_count": 2,
            "frag_count": 1,
            "depleted_count": 1,
            "error_loops_3": 1,
            "mentor_sla": 14,
            "csi": 4.4,
            "lxd_param": "Субъективная ценность",
            "root_cause": "Интересные прикладные задачи, связность сохранена."
        },
        {
            "cohort_num": 1,
            "cohort_name": "Поток 1",
            "module_num": 4,
            "module_name": "M4: Аутентичный выпускной кейс",
            "cor": 0.67,
            "drop_count": 1,
            "rushed_count": 2,
            "frag_count": 1,
            "depleted_count": 2,
            "error_loops_3": 2,
            "mentor_sla": 15,
            "csi": 4.5,
            "lxd_param": "Субъективный контроль",
            "root_cause": "Защита самостоятельного проекта."
        },

        # --- ПОТОК 2 ---
        {
            "cohort_num": 2,
            "cohort_name": "Поток 2",
            "module_num": 1,
            "module_name": "M1: Введение и базовый синтаксис",
            "cor": 0.93,
            "drop_count": 1,
            "rushed_count": 1,
            "frag_count": 0,
            "depleted_count": 0,
            "error_loops_3": 1,
            "mentor_sla": 14,
            "csi": 4.7,
            "lxd_param": "Трение среды",
            "root_cause": "Один студент застрял на настройке локального окружения."
        },
        {
            "cohort_num": 2,
            "cohort_name": "Поток 2",
            "module_num": 2,
            "module_name": "M2: Алгоритмы и структуры данных",
            "cor": 0.64,
            "drop_count": 4,
            "rushed_count": 6,
            "frag_count": 4,
            "depleted_count": 3,
            "error_loops_3": 5,
            "mentor_sla": 38,
            "csi": 3.3,
            "lxd_param": "Субъективный контроль & Срывы",
            "root_cause": "Разрыв теории и практики + задержка код-ревью ментором (38 ч). Серии 3+ ошибок вызвали переход в безнадежность."
        },
        {
