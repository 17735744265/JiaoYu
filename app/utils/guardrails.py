"""
============================================
安全过滤与防护（Guardrails）
============================================

【讲解】这是Agent的"安全带"——防止Agent说出不该说的话。

为什么需要Guardrails？
1. 敏感信息泄露：用户可能套取其他用户信息
2. 越界操作：用户可能让Agent执行不合理的退款
3. 注入攻击：用户输入恶意Prompt试图改变Agent行为
4. 合规要求：金融、医疗等行业有强制要求

【面试考点】你在项目中怎么处理安全问题？
回答时从这个文件的技术点展开，非常加分。

三层防护：
1. 输入层：过滤用户输入（敏感词、注入检测）
2. 处理层：限制Agent行为（话题限制、操作确认）
3. 输出层：检查Agent输出（敏感信息脱敏）
"""

import re
from config import SENSITIVE_WORDS, MAX_QUERY_LENGTH


class Guardrails:
    """安全过滤器"""
    
    @staticmethod
    def check_input(query: str) -> tuple[bool, str]:
        """
        检查用户输入是否安全
        
        Args:
            query: 用户输入文本
            
        Returns:
            (is_safe, reason): 是否安全 + 不安全的原因
            
        【讲解】输入检查三件事：
        1. 长度限制：防超长输入攻击
        2. 敏感词检测：防套取敏感信息
        3. Prompt注入检测：防恶意指令
        """
        # 1. 长度检查
        if len(query) > MAX_QUERY_LENGTH:
            return False, f"输入过长（{len(query)}字符），请精简描述（最大{MAX_QUERY_LENGTH}字符）"
        
        # 2. 敏感词检查
        for word in SENSITIVE_WORDS:
            if word in query:
                return False, f"输入包含敏感内容，请重新描述您的问题"
        
        # 3. Prompt注入检测
        # 常见的注入模式：
        injection_patterns = [
            r"忽略.*指令",          # "忽略上面的指令"
            r"你现在是",            # "你现在是xxx"
            r"system:",            # 伪系统消息
            r"假装.*是",           # "假装你是管理员"
            r"override",           # 覆盖指令
            r"jailbreak",          # 越狱
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, "检测到异常输入，请正常描述您的问题"
        
        return True, ""
    
    @staticmethod
    def check_output(response: str) -> str:
        """
        检查并过滤Agent输出
        
        Args:
            response: Agent生成的回复
            
        Returns:
            过滤后的安全回复
            
        【讲解】输出过滤主要是脱敏：
        - 手机号中间4位用*替代
        - 身份证号脱敏
        - 银行卡号脱敏
        - 邮箱部分脱敏
        """
        # 手机号脱敏: 13812345678 → 138****5678
        response = re.sub(
            r'(1[3-9]\d)\d{4}(\d{4})',
            r'\1****\2',
            response
        )
        
        # 身份证号脱敏: 110101199001011234 → 110101****1234
        response = re.sub(
            r'(\d{6})\d{8}(\d{4})',
            r'\1********\2',
            response
        )
        
        # 银行卡号脱敏: 6222021234567890 → 6222****7890
        response = re.sub(
            r'(\d{4})\d{8,12}(\d{4})',
            r'\1**********\2',
            response
        )
        
        return response
    
    @staticmethod
    def is_sensitive_operation(tool_name: str, arguments: dict) -> bool:
        """
        判断是否为敏感操作（需要二次确认）
        
        【讲解】哪些操作需要确认？
        - 退款：涉及钱
        - 账号变更：涉及安全
        - 大额操作：需要人工审核
        
        这是"人在回路"（Human-in-the-loop）的体现。
        """
        sensitive_tools = ["refund_order"]
        return tool_name in sensitive_tools
