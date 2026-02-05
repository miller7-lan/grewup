import streamlit as st
import pandas as pd
import json
import os
import re

# --- [改动1] 环境兼容：尝试导入本地 Ollama，失败则标记为 False ---
try:
    import ollama
    HAS_LOCAL_OLLAMA = True
except ImportError:
    HAS_LOCAL_OLLAMA = False

# --- [改动1] 引入 OpenAI 用于云端调用 ---
from openai import OpenAI

# ================= 0. 数据持久化核心函数 (保持不变) =================
DATA_FILE = "class_roster.json"

def load_roster():
    """启动时从文件读取名单"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"group_a": [], "group_b": []}
    return {"group_a": [], "group_b": []}

def save_roster(group_a, group_b):
    """保存名单到文件"""
    data = {"group_a": group_a, "group_b": group_b}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ================= 1. 页面配置与样式 (保持不变) =================
st.set_page_config(
    page_title="Dazzle Secretary Pro", 
    page_icon="🌈", 
    layout="wide"
)
st.markdown('<div style="height: 5px; background: linear-gradient(90deg, #FF4B4B 0%, #FFB347 50%, #4B79FF 100%);"></div>', unsafe_allow_html=True)

st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
        <span style="color: #666; font-size: 0.9em;">📅 当前日期：{pd.Timestamp.now().strftime('%Y-%m-%d')}</span>
        <span style="background-color: #ffe8e8; color: #ff4b4b; padding: 2px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">
            🚀 Designed By Dazzle With MacBook 
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stProgress > div > div > div > div { background-color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. 核心 AI 提取函数 (核心改动) =================
def extract_names_ai(text, model_name):
    """
    智能路由：本地优先，失败自动降级到云端 API
    """
    # 保持你认可的强力清洗 Prompt
    prompt = (
        "你是一个专业的考勤核对助手。请从乱序文本中提取所有中国人的姓名。\n"
        "⚠️ 严格清洗规则：\n"
        "1. 去除名字中间或周围的数字、空格、标点、表情（如 '刘骐1豪' -> '刘骐豪'）。\n"
        "2. 忽略非人名文本（如'已完成'、'截图'）。\n"
        "3. 仅返回 JSON 字符串数组，不要Markdown格式。\n"
        f"待处理文本：\n{text}"
    )
    
    content = ""
    
    # --- 分支 A: 尝试本地 Ollama ---
    if HAS_LOCAL_OLLAMA and "Cloud" not in model_name:
        try:
            # 如果选的是云端选项，就不走这里；否则尝试本地
            response = ollama.generate(model=model_name, prompt=prompt)
            content = response['response'].strip()
        except Exception:
            pass # 本地失败，静默进入分支 B

    # --- 分支 B: 云端 DeepSeek API (当本地失败或无环境时) ---
    if not content:
        api_key = st.secrets.get("DEEPSEEK_API_KEY") # 从 Streamlit 后台读取
        if not api_key:
            st.error("⚠️ 未检测到本地 Ollama，且未配置云端 API Key！")
            return []
            
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            content = response.choices[0].message.content.strip()
            st.toast("☁️ 已切换至云端 DeepSeek 引擎") # 提示一下用户
        except Exception as e:
            st.error(f"云端调用失败: {e}")
            return []

    # --- 通用清洗逻辑 (保持不变) ---
    try:
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        
        start, end = content.find('['), content.rfind(']') + 1
        names = json.loads(content[start:end])
        
        cleaned_names = []
        for n in names:
            pure_name = re.sub(r'[^\u4e00-\u9fa5]', '', n)
            if len(pure_name) >= 2:
                cleaned_names.append(pure_name)
        return list(set(cleaned_names))
    except:
        return []

# ================= 3. 数据初始化 (保持不变) =================
if "group_a" not in st.session_state or "group_b" not in st.session_state:
    saved_data = load_roster()
    st.session_state.group_a = saved_data.get("group_a", [])
    st.session_state.group_b = saved_data.get("group_b", [])

# ================= 4. 侧边栏 (轻微改动以适应云端) =================
with st.sidebar:
    st.title("🌈 考勤看板")
    
    # --- [改动3] 模型选择加了容错 ---
    try:
        if HAS_LOCAL_OLLAMA:
            models_info = ollama.list()
            model_list = [m['name'] for m in (models_info['models'] if 'models' in models_info else models_info)]
            # 自动找 qwen3
            default_index = 0
            for i, name in enumerate(model_list):
                if "qwen3" in name.lower():
                    default_index = i
                    break
            selected_model = st.selectbox("🧠 选择 AI 大脑:", model_list, index=default_index)
        else:
            # 云端环境直接显示这个，不报错
            selected_model = st.selectbox("🧠 选择 AI 大脑:", ["☁️ DeepSeek V3 (Cloud)"])
    except:
        selected_model = st.selectbox("🧠 选择 AI 大脑:", ["☁️ DeepSeek V3 (Cloud)"])
    
    st.divider()
    count_a = len(st.session_state.group_a)
    count_b = len(st.session_state.group_b)
    st.subheader("📊 班级基数")
    st.write(f"团员总数:**{count_a}**人")
    st.write(f"群众总数:**{count_b}** 人")
    st.write(f"全班总计:**{count_a + count_b}** 人")
    
    st.divider()
    st.subheader("⌨️ 技术栈说明")
    st.markdown("""
    - **核心语言**: Python 3.13
    - **AI 引擎**: Ollama / DeepSeek API
    - **交互框架**: Streamlit Pro
    - **硬件优化**: M4 Apple Silicon 加速
    """)
    st.divider()
    # ... (原有 expanader 保持不变) ...
    with st.expander("🔍 智能核查 (AI Check)"):
        st.markdown("- 大模型解析：Qwen/DeepSeek 驱动\n- 多范围切换：适配团课/签到")
    with st.expander("🧼 自动化清洗 (Clean)"):
        st.markdown("- 底册去重\n- 冲突自动修正")
    with st.expander("📊 实时看板 (Dashboard)"):
        st.markdown("- 四维指标计算\n- 一键生成催办名单")

# ================= 5. 主界面布局 (保持不变) =================
st.title("🛡️ 团支部智能核查系统")

tab_check, tab_config = st.tabs(["🚀 智能核查", "⚙️ 底册管理"])

# --- Tab 1: 智能核查 (保持极速模式逻辑) ---
with tab_check:
    if not st.session_state.group_a and not st.session_state.group_b:
        st.warning("⚠️ 请先切换到『底册管理』录入班级名单！")
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            mode = st.radio("核查范围：", ["仅核查团员", "全班核查"], horizontal=True)
        with c2:
            st.write("")
            use_turbo = st.toggle("⚡ 极速匹配模式", value=True, help="关闭 AI，使用纯算法匹配")
        
        target_list = st.session_state.group_a if "仅" in mode else (st.session_state.group_a + st.session_state.group_b)
        
        raw_text = st.text_area("📥 粘贴完成情况（乱序文本/截图识字）：", height=180, placeholder="例如：1.张三 2.李四 已完成...")
        
        btn_label = "⚡ 立即秒杀" if use_turbo else "🔍 开始 AI 深度核查"
        
        if st.button(btn_label):
            if not raw_text:
                st.warning("请先粘贴内容！")
            else:
                if use_turbo:
                    # 极速模式
                    with st.spinner("⚡ 正在执行 O(N) 极速检索..."):
                        clean_text = re.sub(r'[^\u4e00-\u9fa5]', '', raw_text)
                        valid_done = []
                        for name in target_list:
                            if name in raw_text or name in clean_text:
                                valid_done.append(name)
                        valid_done = set(valid_done)
                        extracted_names = list(valid_done)
                else:
                    # AI 模式
                    with st.spinner(f"正在驱动 AI 深度解析..."):
                        extracted_names = extract_names_ai(raw_text, selected_model)
                        valid_done = set(target_list) & set(extracted_names)

                # --- 结果展示 (保持不变) ---
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
                        st.markdown(f"#### <span style='color: #ff4b4b;'>🚩 待冲锋 ({miss_n})</span>", unsafe_allow_html=True)
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
                            done_tags = " ".join([f'<span style="background-color:#e1f5fe; color:#01579b; padding:2px 8px; border-radius:10px; margin:2px; display:inline-block;">{n}</span>' for n in sorted(list(valid_done))])
                            st.markdown(done_tags, unsafe_allow_html=True)
                        else:
                            st.info("暂无匹配数据")

# --- Tab 2: 底册管理 (保持不变) ---
with tab_config:
    st.subheader("📝 录入/更新班级底册")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🔴 团员名单")
        input_a = st.text_area("每行一个名字", value="\n".join(st.session_state.group_a), height=300, key="edit_a")
    with col_b:
        st.markdown("### 🔵 群众名单")
        input_b = st.text_area("每行一个名字", value="\n".join(st.session_state.group_b), height=300, key="edit_b")
    
    if st.button("🚀 保存并自动清洗底册数据"):
        clean_a = list(dict.fromkeys([n.strip() for n in input_a.split("\n") if n.strip()]))
        raw_b = list(dict.fromkeys([n.strip() for n in input_b.split("\n") if n.strip()]))
        set_a = set(clean_a)
        clean_b = [name for name in raw_b if name not in set_a]
        
        st.session_state.group_a = clean_a
        st.session_state.group_b = clean_b
        save_roster(clean_a, clean_b) 
        st.success("✅ 数据已保存！")
        st.rerun()

# ================= 6. 页脚 (保持不变) =================
st.markdown("---")
st.markdown("<center style='color:gray; font-size:0.8em;'>河南大学 2025 级全体软件工程班委专用<br>Dazzle M4 Silicon Powered</center>", unsafe_allow_html=True)