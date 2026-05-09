import streamlit as st
import pandas as pd
import ollama

from agent import AttendanceAgent
from history import clear_history, load_history, save_history_item
from ocr import extract_text_from_image, ocr_status_message
from roster import clean_name_lines, load_roster, save_roster, target_names

# ================= 1. 页面配置与样式 =================
st.set_page_config(
    page_title="Dazzle Secretary Pro",
    page_icon="🌈",
    layout="wide"
)
st.markdown("""
    <style>
    .block-container { padding-top: 1.6rem; max-width: 1180px; }
    .app-hero {
        position: relative;
        border: 1px solid #ffd6d6;
        border-radius: 8px;
        padding: 20px 24px 24px;
        background:
            linear-gradient(135deg, rgba(255, 245, 245, 0.96), rgba(239, 246, 255, 0.98)),
            #ffffff;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.08);
        margin-bottom: 18px;
        overflow: hidden;
    }
    .app-hero:after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff4b4b 0%, #ffb347 36%, #2dd4bf 68%, #4b79ff 100%);
    }
    .hero-topline {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        color: #7a5c5c;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .hero-title {
        margin: 0;
        font-size: 34px;
        line-height: 1.14;
        color: #202124;
        font-weight: 780;
        letter-spacing: 0;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 20px;
    }
    .status-card {
        border: 1px solid #ffe1e1;
        border-radius: 8px;
        padding: 14px 16px;
        background: #fff;
        box-shadow: 0 8px 22px rgba(75, 121, 255, 0.06);
    }
    .status-label {
        color: #667085;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .status-value {
        color: #ff4b4b;
        font-size: 28px;
        font-weight: 760;
        line-height: 1.1;
    }
    .status-note {
        color: #667085;
        font-size: 12px;
        margin-top: 4px;
    }
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        margin: 3px;
        font-size: 14px;
        border: 1px solid transparent;
    }
    .tag-missing { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
    .tag-done { background: #ecfdf3; color: #027a48; border-color: #abefc6; }
    .tag-unknown { background: #fffaeb; color: #b54708; border-color: #fedf89; }
    .result-banner {
        border-radius: 8px;
        padding: 16px 18px;
        border: 1px solid #ffd6d6;
        background: #fff7ed;
        margin: 16px 0;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e8eaef;
        padding: 12px;
        border-radius: 8px;
    }
    .stProgress > div > div > div > div { background-color: #ff4b4b; }
    @media (max-width: 820px) {
        .status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .hero-title { font-size: 28px; }
    }
    </style>
    """, unsafe_allow_html=True)


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

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""


def render_tag_list(names, css_class):
    if not names:
        return ""
    return "".join([f'<span class="tag {css_class}">{name}</span>' for name in names])


def result_csv(result):
    rows = ["status,name"]
    rows.extend([f"done,{name}" for name in result.done])
    rows.extend([f"missing,{name}" for name in result.missing])
    rows.extend([f"unknown,{name}" for name in result.unknown])
    return "\n".join(rows)


count_party = len(st.session_state.group_party)
count_a = len(st.session_state.group_a)
count_b = len(st.session_state.group_b)
total_students = count_party + count_a + count_b


# ================= 4. 侧边栏：状态监控 =================
with st.sidebar:
    st.title("Dazzle Secretary")
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

    st.subheader("班级底册")
    st.metric("全班总计", f"{total_students} 人")
    st.write(f"党员：**{count_party}**")
    st.write(f"团员：**{count_a}**")
    st.write(f"群众：**{count_b}**")

    st.divider()
    st.caption("v3.3 Agent Workbench")
    st.caption(ocr_status_message())


# ================= 5. 主界面布局 =================
st.markdown(f"""
    <section class="app-hero">
        <div class="hero-topline">
            <span>📅 {pd.Timestamp.now().strftime('%Y-%m-%d')} · Dazzle Secretary Pro v3.3</span>
            <span>🚀 Designed By Dazzle With MacBook</span>
        </div>
        <h1 class="hero-title">🛡️ 团支部智能核查系统</h1>
    </section>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="status-grid">
        <div class="status-card"><div class="status-label">🟡 党员</div><div class="status-value">{count_party}</div><div class="status-note">优先身份</div></div>
        <div class="status-card"><div class="status-label">🔴 团员</div><div class="status-value">{count_a}</div><div class="status-note">专项核查</div></div>
        <div class="status-card"><div class="status-label">🔵 群众</div><div class="status-value">{count_b}</div><div class="status-note">全班核查</div></div>
        <div class="status-card"><div class="status-label">🌈 底册总数</div><div class="status-value">{total_students}</div><div class="status-note">自动去重</div></div>
    </div>
""", unsafe_allow_html=True)


tab_check, tab_config, tab_history = st.tabs(["🚀 智能核查", "⚙️ 底册管理", "📚 核查记录"])

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

        current_roster = {
            "group_party": st.session_state.group_party,
            "group_a": st.session_state.group_a,
            "group_b": st.session_state.group_b,
        }
        target_list = target_names(current_roster, mode)
        st.caption(f"当前范围应核查 {len(target_list)} 人；解析引擎：{'极速匹配' if use_turbo else selected_model}")

        st.markdown("#### 🖼️ 截图识别")
        image_file = st.file_uploader(
            "上传群接龙截图、名单图片或 OCR 截图（Mac/Windows 专用 OCR）",
            type=["png", "jpg", "jpeg", "heic", "webp"],
            label_visibility="collapsed",
        )
        ocr_col1, ocr_col2 = st.columns([1, 3])
        with ocr_col1:
            run_ocr = st.button("识别图片文字", disabled=image_file is None)
        with ocr_col2:
            st.caption(ocr_status_message())

        if run_ocr and image_file is not None:
            try:
                with st.spinner("正在识别图片文字..."):
                    st.session_state.ocr_text = extract_text_from_image(
                        image_file.getvalue(),
                        filename=image_file.name,
                    )
                st.success("图片文字已识别，可继续核查。")
            except Exception as exc:
                st.error(str(exc))

        raw_text = st.text_area(
            "📥 粘贴或识别完成情况文本：",
            value=st.session_state.ocr_text,
            height=180,
            placeholder="例如：1.张三 2.李四 已完成...",
        )

        btn_label = "⚡ 立即秒杀 (0延迟)" if use_turbo else "🔍 启动 AI 深度解析"

        if st.button(btn_label):
            if not raw_text:
                st.warning("请先粘贴内容！")
            else:
                agent = AttendanceAgent(selected_model)
                spinner_text = "⚡ 正在执行极速检索..." if use_turbo else f"正在驱动 {selected_model} 深度提取 (速度较慢)..."
                with st.spinner(spinner_text):
                    result = agent.check(raw_text, target_list, use_ai=not use_turbo)
                saved_history = save_history_item(mode, result)

                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                total_n = result.total
                done_n = result.done_count
                miss_n = result.missing_count
                percent = result.percent

                m1.metric("应到人数", f"{total_n}人")
                m2.metric("实到人数", f"{done_n}人", delta=f"{done_n - total_n}", delta_color="inverse")
                m3.metric("待冲锋", f"{miss_n}人", delta=f"{miss_n}", delta_color="off")
                m4.metric("完成率", f"{percent:.1f}%")
                st.progress(percent / 100)
                st.markdown(f"""
                    <div class="result-banner">
                        <strong>{mode}</strong> · {result.source} · 完成率 {percent:.1f}% ·
                        已完成 {done_n} 人，未完成 {miss_n} 人
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("### 📋 核查详情")
                with st.container(border=True):
                    res_col1, res_col2 = st.columns(2)

                    with res_col1:
                        st.markdown(f"#### <span style='color: #ff4b4b;'>🚩 未完成名单 ({miss_n})</span>", unsafe_allow_html=True)
                        if result.missing:
                            st.markdown(render_tag_list(result.missing, "tag-missing"), unsafe_allow_html=True)

                            st.divider()
                            st.markdown("**📢 快速群通知：**")
                            st.code(result.reminder, language="text")
                        else:
                            st.success("🎉 功德圆满，全员已完成！")

                    with res_col2:
                        st.markdown(f"#### <span style='color: #28a745;'>✅ 已完成名单 ({done_n})</span>", unsafe_allow_html=True)
                        if result.done:
                            st.markdown(render_tag_list(result.done, "tag-done"), unsafe_allow_html=True)
                        else:
                            st.info("暂无匹配数据")

                        if result.unknown:
                            st.caption("以下姓名被识别出来，但不在当前核查范围内：")
                            st.markdown(render_tag_list(result.unknown, "tag-unknown"), unsafe_allow_html=True)

                st.download_button(
                    "下载本次核查 CSV",
                    data=result_csv(result),
                    file_name=f"attendance_{saved_history['time'].replace(':', '-')}.csv",
                    mime="text/csv",
                )
                st.caption(f"本次解析来源：{result.source}，已写入核查记录。")


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
        clean_party = clean_name_lines(input_party)
        clean_a = clean_name_lines(input_a)
        clean_b = clean_name_lines(input_b)

        saved = save_roster(clean_party, clean_a, clean_b)

        st.session_state.group_party = saved["group_party"]
        st.session_state.group_a = saved["group_a"]
        st.session_state.group_b = saved["group_b"]

        st.success("✅ 数据已自动清洗并同步至看板！")
        st.rerun()


with tab_history:
    history_items = load_history()
    c_history_title, c_history_action = st.columns([3, 1])
    with c_history_title:
        st.subheader("最近核查记录")
    with c_history_action:
        if history_items and st.button("清空记录"):
            clear_history()
            st.rerun()

    if not history_items:
        st.info("还没有核查记录。完成一次核查后，这里会自动保存摘要。")
    else:
        for item in history_items[:10]:
            with st.container(border=True):
                top_l, top_r = st.columns([3, 1])
                with top_l:
                    st.markdown(f"**{item['time']} · {item['mode']}**")
                    st.caption(f"{item['source']} · 完成率 {item['percent']}%")
                with top_r:
                    st.metric("未完成", f"{item['missing_count']} 人")

                if item["missing"]:
                    st.markdown(render_tag_list(item["missing"], "tag-missing"), unsafe_allow_html=True)
                    st.code(item["reminder"], language="text")
                else:
                    st.success("本次全员完成")


# ================= 6. 页脚 =================
st.markdown("---")
st.markdown("<center style='color:gray; font-size:0.8em;'>河南大学 2025 级全体软件工程班委专用<br>Dazzle M4 Silicon Powered</center>", unsafe_allow_html=True)
