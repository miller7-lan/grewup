import streamlit as st
import ollama
import json

# ================= 1. 核心数据库 =================
# 32名团员名单 (Group A)
GROUP_A = ["晏宁", "陈子炫", "龚嘉杰", "翟金铭", "李硕俣", "卢曦翔", "卢文宇", "邓淇畅", "杨锦坤", "吴凡", "梅振凯", "李鑫宇", "林俊宇", "石文浚", "涂真", "罗文佳成", "刘君泽", "刘骐豪", "尹鹏智", "王缘龙", "黄振宇", "冯子玺", "梁晨", "赵介榕", "吴文泽", "贾晓宇", "薛文博", "付应玺", "王玉玺", "刘娜辰", "李欣然", "高睿恺"]
# 16名群众名单
OTHER_STUDENTS = ["李阳", "李鼎垚", "赵子锐", "胡贻炫", "凌致均", "毛瀚增", "陈梦琦", "崔溪桐", "刘锐", "杨博", "邓李菲", "韦创鑫", "王记星", "杨登杰", "李佳小敏", "朱芮蝶"]
ALL_STUDENTS = GROUP_A + OTHER_STUDENTS

# ================= 2. 核心功能函数 =================

@st.cache_data(show_spinner=False)
def extract_names_with_ollama(text, model_name):
    """利用本地 Ollama 提取人名，启用缓存提速"""
    prompt = f"请从文本中提取出所有人名，并仅以 JSON 数组格式返回，如 ['姓名1', '姓名2']。不要解释。文本：\n{text}"
    try:
        response = ollama.generate(model=model_name, prompt=prompt)
        content = response['response'].strip()
        # 清洗可能出现的 Markdown 标签
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        start, end = content.find('['), content.rfind(']') + 1
        return json.loads(content[start:end])
    except Exception as e:
        st.error(f"AI 引擎调用失败: {e}")
        return []

# ================= 3. UI 界面统一化 =================

st.set_page_config(page_title="Dazzle Secretary Pro", page_icon="🌈", layout="wide")

# 自定义 CSS 提升美观度
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #FF4B4B; color: white; }
    .sidebar-text { font-size: 0.9em; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏设计 ---
with st.sidebar:
    st.title("🌈 控制中心")
    st.markdown(f"**负责人：** 陈子炫 (Dazzle)") #
    st.markdown(f"**身份：** 25级软工7班团支书") #
    st.divider()

    # 获取并选择模型
    try:
        models_info = ollama.list()
        model_list = [m['name'] for m in (models_info['models'] if 'models' in models_info else models_info)]
    except:
        model_list = ["dazzle-secretary:latest", "qwen3:8b"]
    
    selected_model = st.selectbox("🧠 选择 AI 大脑 (Model):", model_list)
    
    st.divider()
    # 统计面板
    col1, col2 = st.columns(2)
    col1.metric("班级人数", len(ALL_STUDENTS))
    col2.metric("团员人数", len(GROUP_A))
    
    # 技术栈看板
    st.divider()
    st.markdown("### 🛠️ 技术栈 (Tech Stack)")
    st.markdown(f"""
    <div class="sidebar-text">
    • Language: Python 3.13<br>
    • Framework: Streamlit<br>
    • AI: Ollama Local LLM<br>
    • Hardware: M4 Apple Silicon
    </div>
    """, unsafe_allow_html=True) #

# --- 主界面设计 ---
st.title("🛡️ Dazzle-Secretary 智能核查系统")
st.caption("基于本地 AI 引擎开发，服务 2025 级软件工程 7 班团支部")

# 模式选择
mode = st.radio("请选择核查范围：", ["全体同学 (48人)", "仅团员 (32人)"], horizontal=True)
target_list = ALL_STUDENTS if "全体" in mode else GROUP_A

# 名单输入
input_text = st.text_area("📥 粘贴已完成人员名单（支持乱序文本、截图识别文字）：", height=200)

if st.button("🚀 开始智能比对"):
    if not input_text:
        st.warning("请先粘贴名单！")
    else:
        with st.spinner(f"正在驱动 {selected_model} 进行逻辑核查..."):
            parsed_names = extract_names_with_ollama(input_text, selected_model)
            
            if parsed_names:
                base_set = set(target_list)
                done_set = set(name.strip() for name in parsed_names)
                valid_done = base_set & done_set
                missing = sorted(list(base_set - valid_done))
                
                st.divider()
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    if not missing:
                        st.balloons()
                        st.success("🎉 全部完成，辛苦了！")
                    else:
                        st.error(f"❌ 未完成名单 ({len(missing)}人)")
                        # 统一格式：使用 write 直接展示列表，生成与右边一致的交互式索引视图
                        st.write(missing) 
                        # 如果需要一键复制的话术，可以保留一个精简的 code 块在最下面
                        st.caption("复制下方话术去群里 @ 他们：")
                        st.code("、".join(missing), language="text")
                
                with res_col2:
                    st.success(f"✅ 已匹配成功 ({len(valid_done)}人)")
                    # 保持一致
                    st.write(list(valid_done))

# 页脚
st.markdown("---")
st.markdown("<center style='color:gray; font-size:0.8em;'>河南大学 2025 级软件工程 7 班团支部专用<br>Dazzle M4 Silicon Powered</center>", unsafe_allow_html=True) #