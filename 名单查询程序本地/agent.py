import json
import re

import ollama

from attendance import build_attendance_result, extract_by_turbo_match
from roster import normalize_name


class AttendanceAgent:
    """Small agent wrapper that chooses a parsing tool and returns verifiable results."""

    def __init__(self, model_name):
        self.model_name = model_name

    def check(self, raw_text, target_list, use_ai=False):
        if use_ai:
            extracted = self.extract_names_ai(raw_text)
            return build_attendance_result(target_list, extracted, source=f"AI: {self.model_name}")

        extracted, corrections = extract_by_turbo_match(raw_text, target_list)
        source = "极速匹配 + 姓名纠错" if corrections else "极速匹配"
        return build_attendance_result(target_list, extracted, source=source, corrections=corrections)

    def extract_names_ai(self, text):
        prompt = (
            "你是一个专业的考勤核对助手。请从下方乱序文本中提取所有中国人姓名。\n"
            "要求：\n"
            "1. 去除名字中间或周围的数字、空格、标点、表情，例如“刘骐1豪”应为“刘骐豪”。\n"
            "2. 忽略“已完成”“截图”“收到”等非姓名文本。\n"
            "3. 只返回 JSON 字符串数组，例如 [\"张三\", \"李四\"]。\n"
            "4. 不要返回 Markdown，不要解释。\n"
            f"待处理文本：\n{text}"
        )

        try:
            response = ollama.generate(model=self.model_name, prompt=prompt)
            content = response["response"].strip()
            names = self._parse_name_array(content)
        except Exception as exc:
            print(f"AI Error: {exc}")
            return []

        cleaned = []
        for name in names:
            pure_name = normalize_name(name)
            if len(pure_name) >= 2:
                cleaned.append(pure_name)
        return list(dict.fromkeys(cleaned))

    @staticmethod
    def _parse_name_array(content):
        content = re.sub(r"```(?:json)?", "", content).replace("```", "").strip()
        start = content.find("[")
        end = content.rfind("]") + 1
        if start < 0 or end <= 0:
            return []

        data = json.loads(content[start:end])
        if not isinstance(data, list):
            return []
        return data
