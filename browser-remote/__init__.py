# OpenClaw 

"""
OpenClaw Browser远程浏览器控制包 Remote Control Package

让 OpenClaw AI 能够远程操作 Chrome 浏览器。
"""

from .client import RemoteBrowser
from .openclaw_integration import OpenClawBrowser

__version__ = '1.0.0'
__all__ = ['RemoteBrowser', 'OpenClawBrowser']
