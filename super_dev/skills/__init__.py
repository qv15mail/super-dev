"""
Skill 管理模块
"""

from .manager import SkillManager
from .skill_template import SUPER_DEV_VERSION, SkillFrontmatter, SkillTemplate, SuperDevSkillContent

__all__ = [
    "SUPER_DEV_VERSION",
    "SkillFrontmatter",
    "SkillManager",
    "SkillTemplate",
    "SuperDevSkillContent",
]
