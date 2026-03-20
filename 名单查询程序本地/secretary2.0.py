import streamlit as st
import pandas as pd
import ollama
import json
import os


# ================= 0. 数据持久化核心函数 (新增) =================
DATA_FILE = "class_roster.json"  # 定义存储文件名为 class_roster.json


def load_roster():
    """启动时从文件读取名单"""
    default_data = {"group_party": [], "group_a": [], "group_b": []}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "group_party": data.get("group_party", []),
                "group_a": data.get("group_a", []),
                "group_b": data.get("group_b", []),
            }
        except Exception:
            return default_data
    return default_data


def save_roster(group_party, group_a, group_b):
    """保存名单到文件"""
    data = {"group_party": group_party, "group_a": group_a, "group_b": group_b}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ================= 1. 页面配置与样式 =================
st.set_page_config(
    page_title="Dazzle Secretary Pro",
    page_icon="🌈",
    layout="wide"
)
# 顶部彩色条装饰
st.markdown('<div style="height: 5px; background: linear-gradient(90deg, #FF4B4B 0%, #FFB347 50%, #4B79FF 100%);"></div>', unsafe_allow_html=True)

# 动态副标题 (ENFJ 属性的小彩蛋)
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
        <span style="color: #666; font-size: 0.9em;">📅 当前日期：{pd.Timestamp.now().strftime('%Y-%m-%d')}</span>
        <span style="background-color: #ffe8e8; color: #ff4b4b; padding: 2px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">
            🚀 Designed By Dazzle With MacBook
        </span>
    </div>
""", unsafe_allow_html=True)

# 自定义简单的 CSS 让界面更专业
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stProgress > div > div > div > div { background-color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)


# ================= 2. 核心 AI 提取函数 =================
def extract_names_ai(text, model_name):
    """
    AI 提取 + 强力清洗模式
    """
    prompt = (
        "你是一个专业的考勤核对助手。请从下方的乱序文本中提取所有中国人的姓名。\n"
        "⚠️ 严格遵守以下清洗规则：\n"
        "1. 去除名字中间或周围的所有数字、空格、标点符号、表情（如 '刘骐1豪' -> '刘骐豪'，'李 欣然' -> '李欣然'）。\n"
        "2. 忽略非人名的普通文本（如'已完成'、'截图'）。\n"
        "3. 仅返回一个纯 JSON 字符串数组，不要包含 Markdown 格式或任何解释。\n"
        f"待处理文本：\n{text}"
    )

    try:
        response = ollama.generate(model=model_name, prompt=prompt)
        content = response['response'].strip()

        if "```" in content:
            content = content.replace("```json", "").replace("```", "")

        start, end = content.find('['), content.rfind(']') + 1
        if start == -1 or end == -1:
            return []

        names = json.loads(content[start:end])

        import re
        cleaned_names = []
        for n in names:
            pure_name = re.sub(r'[^\u4e00-\u9fa5]', '', n)
            if len(pure_name) >= 2:
                cleaned_names.append(pure_name)

        return list(set(cleaned_names))

    except Exception as e:
        print(f"AI Error: {e}")
        return []


# ================= 3. 数据持久化初始化 (修改版) =================
if (
    "group_party" not in st.session_state
    or "group_a" not in st.session_state
    or "group_b" not in st.session_state
):
    saved_data = load_roster()
    st.session_state.group_party = saved_data.get("group_party", [])
    st.session_state.group_a = saved_data.get("group_a", [])
    st.session_state.group_b = saved_data.get("group_b", [])


# ================= 4. 侧边栏：状态监控 =================
with st.sidebar:
    st.title("🌈 考勤看板")
    try:
        models_info = ollama.list()
        model_list = [m['name'] for m in (models_info['models'] if 'models' in models_info else models_info)]

        default_index = 0
        for i, name in enumerate(model_list):
            if "qwen3" in name.lower():
                default_index = i
                break
        selected_model = st.selectbox("🧠 选择 AI 大脑:", model_list, index=default_index)
    except Exception:
        selected_model = st.selectbox("🧠 选择 AI 大脑:", ["qwen3:8b", "dazzle-secretary"])

    st.divider()

    count_party = len(st.session_state.group_party)
    count_a = len(st.session_state.group_a)
    count_b = len(st.session_state.group_b)
    st.subheader("📊 班级基数")
    st.write(f"党员总数:**{count_party}**人")
    st.write(f"团员总数:**{count_a}**人")
    st.write(f"群众总数:**{count_b}**人")
    st.write(f"全班总计:**{count_party + count_a + count_b}**人")

    st.divider()
    st.subheader("⌨️ 技术栈说明")
    st.markdown("""
    - **核心语言**: Python 3.13
    - **AI 引擎**: Ollama + Qwen 3.0 (阿里通义千问)
    - **交互框架**: Streamlit Pro
    - **硬件优化**: M4 Apple Silicon 加速
    """)

    st.divider()
    st.markdown("### 🛠️ 核心功能说明")

    with st.expander("🔍 智能核查 (AI Check)"):
        st.markdown("""
        - **大模型解析**：利用 Ollama 引擎（如 Qwen 3.0）自动从乱序文本、截图识字中精准提取人名。
        - **多范围切换**：支持“仅党员”“仅团员”或“全班”核查，灵活适配不同场景。
        """)

    with st.expander("🧼 自动化清洗 (Clean)"):
        st.markdown("""
        - **底册去重**：录入名单时自动剔除重复项，保持底册唯一性。
        - **冲突纠正**：若同一人出现在不同组别，系统自动按“党员 > 团员 > 群众”保留身份。
        - **静默过滤**：核查时自动过滤多次提交的干扰信息。
        """)

    with st.expander("📊 实时看板 (Dashboard)"):
        st.markdown("""
        - **四维指标**：实时计算应到、实到、未到及完成率。
        - **一键催办**：针对未完成人员，系统自动生成带 @ 符号的群通知话术。
        """)


# ================= 5. 主界面布局 =================
st.title("🛡️ 团支部智能核查系统")


tab_check, tab_config = st.tabs(["🚀 智能核查", "⚙️ 底册管理"])

# --- Tab 1: 智能核查逻辑 ---
with tab_check:
    if not st.session_state.group_party and not st.session_state.group_a and not st.session_state.group_b:
        st.warning("⚠️ 请先切换到『底册管理』录入班级名单！")
    else:
        c1, c2 = st.columns([3, 2])
        with c1:
            mode = st.radio("核查范围：", ["仅核查党员", "仅核查团员", "全班核查"], horizontal=True)
        with c2:
            st.write("")
            use_turbo = st.toggle("⚡ 极速匹配模式", value=True, help="关闭 AI，直接比对名字，速度极快！适合群接龙或 Excel 复制。")

        if mode == "仅核查党员":
            target_list = st.session_state.group_party
        elif mode == "仅核查团员":
            target_list = st.session_state.group_a
        else:
            target_list = st.session_state.group_party + st.session_state.group_a + st.session_state.group_b

        raw_text = st.text_area("📥 粘贴完成情况（乱序文本/截图识字）：", height=180, placeholder="例如：1.张三 2.李四 已完成...")

        btn_label = "⚡ 立即秒杀 (0延迟)" if use_turbo else "🔍 启动 AI 深度解析"

        if st.button(btn_label):
            if not raw_text:
                st.warning("请先粘贴内容！")
            else:
                if use_turbo:
                    with st.spinner("⚡ 正在执行极速检索..."):
                        import re

                        clean_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', raw_text)

                        valid_done = []
                        for name in target_list:
                            if name in raw_text or name in clean_text:
                                valid_done.append(name)

                        valid_done = set(valid_done)
                else:
                    with st.spinner(f"正在驱动 {selected_model} 深度提取 (速度较慢)..."):
                        extracted_names = extract_names_ai(raw_text, selected_model)
                        valid_done = set(target_list) & set(extracted_names)

                base_set = set(target_list)
                missing = sorted(list(base_set - valid_done))

                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                total_n, done_n, miss_n = len(target_list), len(valid_done), len(missing)
                percent = (done_n / total_n * 100) if total_n > 0 else 0

                m1.metric("应到人数", f"{total_n}人")
                m2.metric("实到人数", f"{done_n}人", delta=f"{done_n - total_n}", delta_color="inverse")
                m3.metric("待冲锋", f"{miss_n}人", delta=f"{miss_n}", delta_color="off")
                m4.metric("完成率", f"{percent:.1f}%")
                st.progress(percent / 100)

                st.markdown("### 📋 核查详情")
                with st.container(border=True):
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.markdown(f"#### <span style='color: #ff4b4b;'>🚩 未完成名单 ({miss_n})</span>", unsafe_allow_html=True)
                        if missing:
                            missing_html = "".join([
                                f'<div style="display:inline-block; background-color:#fff5f5; color:#ff4b4b; border:1px solid #ffcccc; padding:4px 10px; border-radius:5px; margin:3px; font-size:14px;">{name}</div>'
                                for name in missing
                            ])
                            st.markdown(missing_html, unsafe_allow_html=True)

                            st.divider()
                            st.markdown("**📢 快速群通知：**")
                            st.code(f"未完成提醒：@{' @'.join(missing)}", language="text")
                        else:
                            st.success("🎉 功德圆满，全员已完成！")

                    with res_col2:
                        st.markdown(f"#### <span style='color: #28a745;'>✅ 已完成名单 ({done_n})</span>", unsafe_allow_html=True)
                        if valid_done:
                            done_tags = " ".join([
                                f'<span style="background-color:#e1f5fe; color:#01579b; padding:2px 8px; border-radius:10px; margin:2px; display:inline-block;">{n}</span>'
                                for n in sorted(list(valid_done))
                            ])
                            st.markdown(done_tags, unsafe_allow_html=True)
                        else:
                            st.info("暂无匹配数据")


# --- Tab 2: 底册管理逻辑（含自动去重与跨组清洗） ---
with tab_config:
    st.subheader("📝 录入/更新班级底册")
    st.info("直接粘贴名单，系统会自动去重并修正身份冲突（党员身份优先，其次团员）。")

    col_party, col_a, col_b = st.columns(3)
    with col_party:
        st.markdown("### 🟡 党员名单")
        input_party = st.text_area("每行一个名字", value="\n".join(st.session_state.group_party), height=300, key="edit_party")
    with col_a:
        st.markdown("### 🔴 团员名单")
        input_a = st.text_area("每行一个名字", value="\n".join(st.session_state.group_a), height=300, key="edit_a")
    with col_b:
        st.markdown("### 🔵 群众名单")
        input_b = st.text_area("每行一个名字", value="\n".join(st.session_state.group_b), height=300, key="edit_b")

    if st.button("🚀 保存并自动清洗底册数据"):
        clean_party = list(dict.fromkeys([n.strip() for n in input_party.split("\n") if n.strip()]))
        party_set = set(clean_party)

        raw_a = list(dict.fromkeys([n.strip() for n in input_a.split("\n") if n.strip()]))
        clean_a = [name for name in raw_a if name not in party_set]
        set_a = set(clean_a)

        raw_b = list(dict.fromkeys([n.strip() for n in input_b.split("\n") if n.strip()]))
        clean_b = [name for name in raw_b if name not in party_set and name not in set_a]

        st.session_state.group_party = clean_party
        st.session_state.group_a = clean_a
        st.session_state.group_b = clean_b

        save_roster(clean_party, clean_a, clean_b)

        st.success("✅ 数据已自动清洗并同步至看板！")
        st.rerun()


# ================= 6. 页脚 =================
st.markdown("---")
st.markdown("<center style='color:gray; font-size:0.8em;'>河南大学 2025 级全体软件工程班委专用<br>Dazzle M4 Silicon Powered</center>", unsafe_allow_html=True)
