#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu Doc Error Fix - EvoMap Capsule移植

Asset ID: sha256:22e00475cc06d59c44f55beb3a623f43c347ac39f1342e62bce5cfcd5593a63c
GDI Score: 61.9 | Confidence: 0.92

功能：
- 添加输入清理 (sanitizeMarkdown + validateBlocks)
- 自动从 write 降级到 append
- 处理飞书文档 API 常见的 400 BadRequest 错误

触发条件: FeishuDocError, 400BadRequest, append_action_failure
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeishuDocError(Exception):
    """飞书文档错误"""
    pass


class BlockType(Enum):
    """飞书文档块类型"""
    TEXT = "text"
    HEADING1 = "heading1"
    HEADING2 = "heading2"
    HEADING3 = "heading3"
    BULLET = "bullet"
    ORDERED = "ordered"
    CODE = "code"
    QUOTE = "quote"
    DIVIDER = "divider"
    IMAGE = "image"
    TABLE = "table"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fixed_content: Optional[Any] = None


@dataclass
class OperationResult:
    """操作结果"""
    success: bool
    method_used: str  # "write" or "append"
    retry_count: int
    error_message: Optional[str] = None
    response: Optional[Dict] = None


class MarkdownSanitizer:
    """Markdown 清理器"""
    
    # 飞书不支持的 Markdown 扩展
    UNSUPPORTED_PATTERNS = [
        (r'\{\{.*?\}\}', ''),  # 模板语法
        (r'{%.*?%}', ''),       # Jinja2 模板
        (r'<script.*?</script>', ''),  # JavaScript
        (r'<style.*?</style>', ''),    # CSS
    ]
    
    # 需要转义的特殊字符
    SPECIAL_CHARS = {
        '\x00': '',      # null 字符
        '\x01': '',      # 控制字符
        '\x02': '',
        '\x03': '',
        '\x04': '',
        '\x05': '',
        '\x06': '',
        '\x07': '',
        '\x08': '',
        '\x0b': '',
        '\x0c': '',
        '\x0e': '',
        '\x0f': '',
        '\x10': '',
        '\x11': '',
        '\x12': '',
        '\x13': '',
        '\x14': '',
        '\x15': '',
        '\x16': '',
        '\x17': '',
        '\x18': '',
        '\x19': '',
        '\x1a': '',
        '\x1b': '',
        '\x1c': '',
        '\x1d': '',
        '\x1e': '',
        '\x1f': '',
    }
    
    @classmethod
    def sanitize(cls, content: str) -> str:
        """
        清理 Markdown 内容
        
        Args:
            content: 原始 Markdown 内容
            
        Returns:
            清理后的内容
        """
        if not content:
            return ""
        
        # 移除不支持的模板语法
        for pattern, replacement in cls.UNSUPPORTED_PATTERNS:
            if len(pattern) == 2 and isinstance(replacement, str):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                content = re.sub(pattern, replacement, content)
        
        # 处理特殊字符
        for char, replacement in cls.SPECIAL_CHARS.items():
            content = content.replace(char, replacement)
        
        # 规范化换行
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 限制连续空行
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # 限制行长度（飞书限制）
        lines = content.split('\n')
        max_length = 10000  # 飞书单块最大字符数
        processed_lines = []
        for line in lines:
            if len(line) > max_length:
                # 截断并添加警告
                line = line[:max_length] + "..."
                logger.warning(f"[FeishuDocFix] Line truncated to {max_length} chars")
            processed_lines.append(line)
        
        content = '\n'.join(processed_lines)
        
        # 清理前后空白
        content = content.strip()
        
        logger.info(f"[FeishuDocFix] Sanitized content: {len(content)} chars")
        return content
    
    @classmethod
    def escape_special_chars(cls, content: str) -> str:
        """转义特殊字符"""
        # 转义反斜杠（保留 Markdown 语法）
        content = content.replace('\\', '\\\\')
        return content


class BlockValidator:
    """块内容验证器"""
    
    MAX_BLOCK_SIZE = 10000  # 最大块大小
    MAX_BLOCKS = 5000       # 最大块数量
    ALLOWED_STYLES = {'bold', 'italic', 'underline', 'strikethrough', 'code', 'link'}
    
    @classmethod
    def validate_blocks(cls, blocks: List[Dict]) -> ValidationResult:
        """
        验证块内容
        
        Args:
            blocks: 块内容列表
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        if not isinstance(blocks, list):
            errors.append("Blocks must be a list")
            return ValidationResult(is_valid=False, errors=errors)
        
        # 检查块数量
        if len(blocks) > cls.MAX_BLOCKS:
            errors.append(f"Too many blocks: {len(blocks)} > {cls.MAX_BLOCKS}")
        
        validated_blocks = []
        
        for i, block in enumerate(blocks):
            block_result = cls._validate_single_block(block, i)
            errors.extend([f"Block {i}: {e}" for e in block_result.errors])
            warnings.extend([f"Block {i}: {w}" for w in block_result.warnings])
            
            if block_result.fixed_content:
                validated_blocks.append(block_result.fixed_content)
            else:
                validated_blocks.append(block)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            fixed_content=validated_blocks if not is_valid else None
        )
    
    @classmethod
    def _validate_single_block(cls, block: Dict, index: int) -> ValidationResult:
        """验证单个块"""
        errors = []
        warnings = []
        fixed_block = block.copy()
        
        # 检查必需字段
        if 'block_type' not in block:
            errors.append("Missing 'block_type' field")
            return ValidationResult(is_valid=False, errors=errors)
        
        block_type = block.get('block_type')
        
        # 验证块类型
        if block_type not in [bt.value for bt in BlockType]:
            warnings.append(f"Unknown block type: {block_type}")
        
        # 验证内容大小
        content = str(block.get('content', ''))
        if len(content) > cls.MAX_BLOCK_SIZE:
            # 尝试修复：截断内容
            fixed_block['content'] = content[:cls.MAX_BLOCK_SIZE]
            warnings.append(f"Content truncated from {len(content)} to {cls.MAX_BLOCK_SIZE}")
        
        # 验证样式
        if 'style' in block:
            styles = block['style']
            if isinstance(styles, dict):
                for style_key in styles.keys():
                    if style_key not in cls.ALLOWED_STYLES:
                        warnings.append(f"Unknown style: {style_key}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixed_content=fixed_block if warnings else None
        )


class FeishuDocFixer:
    """
    飞书文档错误修复器
    
    主要功能：
    1. 输入清理 - 清理 Markdown 格式
    2. 块验证 - 验证内容块格式
    3. 自动降级 - write 失败时降级到 append
    """
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.sanitizer = MarkdownSanitizer()
        self.validator = BlockValidator()
        self._fallback_count = 0
    
    def sanitize_markdown(self, content: str) -> str:
        """清理 Markdown 内容"""
        return self.sanitizer.sanitize(content)
    
    def validate_blocks(self, blocks: List[Dict]) -> ValidationResult:
        """验证块内容"""
        return self.validator.validate_blocks(blocks)
    
    async def write_document(
        self,
        doc_id: str,
        content: Union[str, List[Dict]],
        write_func: callable,
        append_func: Optional[callable] = None,
        max_retries: int = 3
    ) -> OperationResult:
        """
        写入文档（带降级处理）
        
        Args:
            doc_id: 文档ID
            content: 内容（Markdown 字符串或块列表）
            write_func: 写入函数
            append_func: 追加函数（降级时使用）
            max_retries: 最大重试次数
            
        Returns:
            操作结果
        """
        retry_count = 0
        last_error = None
        
        # 1. 清理输入
        if isinstance(content, str):
            content = self.sanitize_markdown(content)
        else:
            validation = self.validate_blocks(content)
            if not validation.is_valid:
                if validation.fixed_content:
                    content = validation.fixed_content
                    logger.warning(f"[FeishuDocFix] Using fixed content: {len(validation.errors)} errors")
                else:
                    return OperationResult(
                        success=False,
                        method_used="none",
                        retry_count=0,
                        error_message=f"Validation failed: {validation.errors}"
                    )
        
        # 2. 尝试 write 操作
        for attempt in range(max_retries):
            try:
                result = await write_func(doc_id, content) if self._is_async(write_func) else write_func(doc_id, content)
                logger.info(f"[FeishuDocFix] Write successful on attempt {attempt + 1}")
                return OperationResult(
                    success=True,
                    method_used="write",
                    retry_count=attempt,
                    response=result
                )
            except Exception as e:
                last_error = e
                retry_count = attempt + 1
                
                # 检查是否是 400 BadRequest
                if self._is_bad_request(e):
                    logger.warning(f"[FeishuDocFix] BadRequest on attempt {attempt + 1}: {e}")
                    break  # 不重试，直接降级
                
                if attempt < max_retries - 1:
                    logger.warning(f"[FeishuDocFix] Write failed, retrying: {e}")
        
        # 3. 降级到 append
        if append_func:
            logger.info(f"[FeishuDocFix] Falling back to append method")
            self._fallback_count += 1
            
            try:
                # 将内容转换为 append 格式
                append_content = self._convert_to_append_format(content)
                
                result = await append_func(doc_id, append_content) if self._is_async(append_func) else append_func(doc_id, append_content)
                
                logger.info(f"[FeishuDocFix] Append successful")
                return OperationResult(
                    success=True,
                    method_used="append",
                    retry_count=retry_count,
                    response=result
                )
            except Exception as e:
                logger.error(f"[FeishuDocFix] Append also failed: {e}")
                return OperationResult(
                    success=False,
                    method_used="append",
                    retry_count=retry_count,
                    error_message=f"Write failed: {last_error}; Append failed: {e}"
                )
        
        # 4. 全部失败
        return OperationResult(
            success=False,
            method_used="write",
            retry_count=retry_count,
            error_message=str(last_error)
        )
    
    def _is_bad_request(self, error: Exception) -> bool:
        """检查是否是 BadRequest 错误"""
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in [
            '400', 'badrequest', 'bad_request', 'invalid',
            'malformed', 'parse error'
        ])
    
    def _is_async(self, func) -> bool:
        """检查函数是否是异步的"""
        import asyncio
        return asyncio.iscoroutinefunction(func)
    
    def _convert_to_append_format(self, content: Union[str, List[Dict]]) -> List[Dict]:
        """将内容转换为 append 格式"""
        if isinstance(content, list):
            return content
        
        # Markdown 字符串转换为块
        blocks = []
        lines = content.split('\n')
        current_block = {"block_type": "text", "content": ""}
        
        for line in lines:
            line = line.rstrip()
            
            # 标题
            if line.startswith('# '):
                if current_block["content"]:
                    blocks.append(current_block)
                blocks.append({"block_type": "heading1", "content": line[2:]})
                current_block = {"block_type": "text", "content": ""}
            elif line.startswith('## '):
                if current_block["content"]:
                    blocks.append(current_block)
                blocks.append({"block_type": "heading2", "content": line[3:]})
                current_block = {"block_type": "text", "content": ""}
            elif line.startswith('### '):
                if current_block["content"]:
                    blocks.append(current_block)
                blocks.append({"block_type": "heading3", "content": line[4:]})
                current_block = {"block_type": "text", "content": ""}
            # 代码块
            elif line.startswith('```'):
                if current_block["content"]:
                    blocks.append(current_block)
                blocks.append({"block_type": "code", "content": line})
                current_block = {"block_type": "text", "content": ""}
            # 分隔线
            elif line.strip() == '---':
                if current_block["content"]:
                    blocks.append(current_block)
                blocks.append({"block_type": "divider"})
                current_block = {"block_type": "text", "content": ""}
            # 普通文本
            else:
                if current_block["content"]:
                    current_block["content"] += '\n'
                current_block["content"] += line
        
        # 添加最后一个块
        if current_block["content"]:
            blocks.append(current_block)
        
        return blocks
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "fallback_count": self._fallback_count,
            "app_id_configured": self.app_id is not None
        }


# ============ 便捷函数 ============

def sanitize_markdown(content: str) -> str:
    """便捷函数：清理 Markdown"""
    return MarkdownSanitizer.sanitize(content)


def validate_blocks(blocks: List[Dict]) -> ValidationResult:
    """便捷函数：验证块"""
    return BlockValidator.validate_blocks(blocks)


async def safe_write_document(
    doc_id: str,
    content: Union[str, List[Dict]],
    write_func: callable,
    append_func: Optional[callable] = None
) -> OperationResult:
    """便捷函数：安全写入文档"""
    fixer = FeishuDocFixer()
    return await fixer.write_document(doc_id, content, write_func, append_func)


# ============ 使用示例 ============

if __name__ == "__main__":
    print("=" * 60)
    print("Feishu Doc Error Fix - Demo")
    print("=" * 60)
    
    # 1. 测试 Markdown 清理
    print("\n1. 测试 Markdown 清理...")
    
    dirty_content = """
# 标题 {{template_var}}

正常内容

<script>alert('xss')</script>

{% some_jinja %}

非常长的行：""" + "a" * 15000 + """

---

结尾
\x00\x01\x02
    """
    
    clean_content = sanitize_markdown(dirty_content)
    print(f"   原始长度: {len(dirty_content)}")
    print(f"   清理后长度: {len(clean_content)}")
    print(f"   包含 script: {'<script>' in clean_content}")
    
    # 2. 测试块验证
    print("\n2. 测试块验证...")
    
    blocks = [
        {"block_type": "heading1", "content": "标题"},
        {"block_type": "text", "content": "正常文本"},
        {"block_type": "unknown_type", "content": "未知类型"},  # 警告
        {"block_type": "text", "content": "a" * 15000},  # 过长，会被截断
    ]
    
    result = validate_blocks(blocks)
    print(f"   是否有效: {result.is_valid}")
    print(f"   错误: {len(result.errors)}")
    print(f"   警告: {len(result.warnings)}")
    
    # 3. 测试文档写入（模拟）
    print("\n3. 测试文档写入降级...")
    
    async def demo():
        fixer = FeishuDocFixer()
        
        # 模拟 write 失败，append 成功
        async def failing_write(doc_id, content):
            raise Exception("400 BadRequest: invalid block format")
        
        async def success_append(doc_id, content):
            return {"code": 0, "msg": "success"}
        
        result = await fixer.write_document(
            doc_id="test_doc",
            content="# Test\n\nHello World",
            write_func=failing_write,
            append_func=success_append
        )
        
        print(f"   成功: {result.success}")
        print(f"   使用方法: {result.method_used}")
        print(f"   重试次数: {result.retry_count}")
    
    import asyncio
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
