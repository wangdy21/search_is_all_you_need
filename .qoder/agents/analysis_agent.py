import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.config import get_config
from backend.utils.logger import get_logger

logger = get_logger("analysis_agent")


class AnalysisAgent:
    """Wraps LLM APIs (ZhipuAI/DeepSeek) for content analysis and translation."""

    SUPPORTED_PROVIDERS = ("zhipu", "deepseek")

    def __init__(self, provider=None):
        config = get_config()
        self.settings = config.ANALYSIS_SETTINGS
        self.provider = provider or self.settings.get("provider", "zhipu")
        self.max_content_length = self.settings.get("max_content_length", 4000)
        self.temperature = self.settings.get("temperature", 0.7)
        
        # Set default model based on provider
        if self.provider == "deepseek":
            self.model = self.settings.get("deepseek_model", "deepseek-chat")
        else:
            self.model = self.settings.get("zhipu_model", "glm-4-flash")

        self.client = None
        self._init_client(config)

    def _init_client(self, config):
        """Initialize LLM client based on provider."""
        if self.provider == "deepseek":
            api_key = config.DEEPSEEK_API_KEY
            if not api_key:
                logger.warning("DeepSeek API key not configured")
                return
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                logger.info(f"Initialized DeepSeek client with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize DeepSeek client: {e}")
        else:  # zhipu (default)
            api_key = config.ZHIPU_API_KEY
            if not api_key:
                logger.warning("ZhipuAI API key not configured")
                return
            try:
                from zhipuai import ZhipuAI
                self.client = ZhipuAI(api_key=api_key)
                logger.info(f"Initialized ZhipuAI client with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize ZhipuAI client: {e}")

    def _truncate(self, content):
        """Truncate content to max length."""
        if len(content) > self.max_content_length:
            return content[:self.max_content_length] + "...(truncated)"
        return content

    def _call_api(self, prompt):
        """Call LLM API and return text response."""
        if not self.client:
            return None, "API key not configured or client initialization failed"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1500,
            )
            text = response.choices[0].message.content
            return text, None
        except Exception as e:
            logger.error(f"{self.provider} API call failed: {e}")
            return None, str(e)

    def generate_summary(self, content):
        """
        Generate a summary and key points for the given content.

        Returns:
            {"summary": str, "key_points": [str], "error": str|None}
        """
        content = self._truncate(content)
        prompt = (
            "请对以下内容生成一段简洁的中文摘要（不超过200字），"
            "并提取3-5个关键要点，以JSON格式返回：\n"
            '{"summary": "摘要内容", "key_points": ["要点1", "要点2", ...]}\n\n'
            f"内容：\n{content}"
        )

        text, error = self._call_api(prompt)
        if error:
            return {"summary": "", "key_points": [], "error": error}

        try:
            # Try to parse JSON from response
            parsed = self._extract_json(text)
            return {
                "summary": parsed.get("summary", text),
                "key_points": parsed.get("key_points", []),
                "error": None,
            }
        except Exception:
            return {"summary": text, "key_points": [], "error": None}

    def translate_content(self, content, target_lang="zh"):
        """
        Translate content to target language.

        Returns:
            {"translated_text": str, "source_lang": str, "error": str|None}
        """
        content = self._truncate(content)
        lang_name = "中文" if target_lang == "zh" else target_lang
        prompt = (
            f"请将以下内容准确翻译为{lang_name}。"
            "保持专业术语准确，对于关键术语可在翻译后用括号标注英文原文。\n\n"
            f"内容：\n{content}"
        )

        text, error = self._call_api(prompt)
        if error:
            return {"translated_text": "", "source_lang": "unknown", "error": error}

        return {
            "translated_text": text,
            "source_lang": "en",
            "error": None,
        }

    def analyze_paper(self, paper_data):
        """
        Analyze an academic paper in depth.

        Args:
            paper_data: dict with keys like title, abstract, snippet.

        Returns:
            {"abstract": str, "method": str, "innovation": str,
             "results": str, "conclusion": str, "error": str|None}
        """
        title = paper_data.get("title", "")
        abstract = paper_data.get("abstract", "") or paper_data.get("snippet", "")
        content = self._truncate(f"Title: {title}\n\nAbstract: {abstract}")

        prompt = (
            "请分析以下学术论文的关键信息，以JSON格式返回：\n"
            '{"abstract_summary": "摘要概述", "method": "研究方法", '
            '"innovation": "主要创新点", "results": "实验结果", '
            '"conclusion": "结论与局限性"}\n\n'
            f"论文信息：\n{content}"
        )

        text, error = self._call_api(prompt)
        if error:
            return {
                "abstract_summary": "", "method": "", "innovation": "",
                "results": "", "conclusion": "", "error": error,
            }

        try:
            parsed = self._extract_json(text)
            return {
                "abstract_summary": parsed.get("abstract_summary", ""),
                "method": parsed.get("method", ""),
                "innovation": parsed.get("innovation", ""),
                "results": parsed.get("results", ""),
                "conclusion": parsed.get("conclusion", ""),
                "error": None,
            }
        except Exception:
            return {
                "abstract_summary": text, "method": "", "innovation": "",
                "results": "", "conclusion": "", "error": None,
            }

    def _extract_json(self, text):
        """Extract JSON object from text that may contain markdown code blocks."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in code blocks
        import re
        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"\{.*\}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if match.lastindex else match.group(0))
                except (json.JSONDecodeError, IndexError):
                    continue

        raise ValueError("No valid JSON found in response")
