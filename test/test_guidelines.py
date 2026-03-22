#!/usr/bin/env python3
"""测试使用建议接口功能.

测试 guidelines://usage 资源的中英文支持、JSON结构完整性等。
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import _build_guidelines_content, _build_chinese_guidelines, _build_english_guidelines


def test_chinese_guidelines():
    """测试中文指南."""
    print("Testing Chinese guidelines...")
    guidelines = _build_chinese_guidelines()

    # 验证基本结构
    assert "version" in guidelines, "Missing 'version' field"
    assert "last_updated" in guidelines, "Missing 'last_updated' field"
    assert "language" in guidelines, "Missing 'language' field"
    assert guidelines["language"] == "zh", "Language should be 'zh'"
    assert "guidelines" in guidelines, "Missing 'guidelines' field"

    # 验证guidelines内容
    g = guidelines["guidelines"]
    assert "project_naming" in g, "Missing 'project_naming' section"
    assert "recording_practices" in g, "Missing 'recording_practices' section"
    assert "query_workflow" in g, "Missing 'query_workflow' section"
    assert "tag_standards" in g, "Missing 'tag_standards' section"
    assert "best_practices" in g, "Missing 'best_practices' section"

    # 验证project_naming
    pn = g["project_naming"]
    assert "title" in pn, "Missing 'title' in project_naming"
    assert "priority" in pn, "Missing 'priority' in project_naming"
    assert "workflow" in pn, "Missing 'workflow' in project_naming"
    assert "examples" in pn, "Missing 'examples' in project_naming"
    assert len(pn["workflow"]) > 0, "workflow should not be empty"
    assert len(pn["examples"]) > 0, "examples should not be empty"

    # 验证recording_practices
    rp = g["recording_practices"]
    assert "title" in rp, "Missing 'title' in recording_practices"
    assert "sections" in rp, "Missing 'sections' in recording_practices"
    assert len(rp["sections"]) > 0, "sections should not be empty"
    for section in rp["sections"]:
        assert "category" in section, "Missing 'category' in section"
        assert "tool" in section, "Missing 'tool' in section"
        assert "description" in section, "Missing 'description' in section"

    # 验证query_workflow
    qw = g["query_workflow"]
    assert "title" in qw, "Missing 'title' in query_workflow"
    assert "principle" in qw, "Missing 'principle' in query_workflow"
    assert "recommended_flow" in qw, "Missing 'recommended_flow' in query_workflow"
    assert "anti_pattern" in qw, "Missing 'anti_pattern' in query_workflow"

    # 验证tag_standards
    ts = g["tag_standards"]
    assert "title" in ts, "Missing 'title' in tag_standards"
    assert "standard_tags" in ts, "Missing 'standard_tags' in tag_standards"
    assert "tag_limits" in ts, "Missing 'tag_limits' in tag_standards"
    assert len(ts["standard_tags"]) > 0, "standard_tags should not be empty"

    # 验证best_practices
    bp = g["best_practices"]
    assert isinstance(bp, list), "best_practices should be a list"
    assert len(bp) > 0, "best_practices should not be empty"

    print("✅ Chinese guidelines structure test passed!")
    return True


def test_english_guidelines():
    """测试英文指南."""
    print("Testing English guidelines...")
    guidelines = _build_english_guidelines()

    # 验证基本结构
    assert "version" in guidelines, "Missing 'version' field"
    assert "last_updated" in guidelines, "Missing 'last_updated' field"
    assert "language" in guidelines, "Missing 'language' field"
    assert guidelines["language"] == "en", "Language should be 'en'"
    assert "guidelines" in guidelines, "Missing 'guidelines' field"

    # 验证guidelines内容（与中文相同结构）
    g = guidelines["guidelines"]
    assert "project_naming" in g, "Missing 'project_naming' section"
    assert "recording_practices" in g, "Missing 'recording_practices' section"
    assert "query_workflow" in g, "Missing 'query_workflow' section"
    assert "tag_standards" in g, "Missing 'tag_standards' section"
    assert "best_practices" in g, "Missing 'best_practices' section"

    print("✅ English guidelines structure test passed!")
    return True


def test_guidelines_content_builder():
    """测试指南内容构建器."""
    print("Testing guidelines content builder...")

    # 测试中文
    zh_guidelines = _build_guidelines_content("zh")
    assert zh_guidelines["language"] == "zh", "Should return Chinese for 'zh'"

    # 测试英文
    en_guidelines = _build_guidelines_content("en")
    assert en_guidelines["language"] == "en", "Should return English for 'en'"

    # 测试默认（非en参数应返回中文）
    default_guidelines = _build_guidelines_content("fr")
    assert default_guidelines["language"] == "zh", "Should default to Chinese for non-'en'"

    # 测试空字符串
    empty_guidelines = _build_guidelines_content("")
    assert empty_guidelines["language"] == "zh", "Should default to Chinese for empty string"

    print("✅ Guidelines content builder test passed!")
    return True


def test_json_serialization():
    """测试JSON序列化."""
    print("Testing JSON serialization...")

    guidelines = _build_guidelines_content("zh")
    json_str = json.dumps(guidelines, ensure_ascii=False, indent=2)

    # 验证可以反序列化
    parsed = json.loads(json_str)
    assert parsed == guidelines, "JSON serialization/deserialization failed"

    print("✅ JSON serialization test passed!")
    return True


def test_tag_standards_completeness():
    """测试标签标准完整性."""
    print("Testing tag standards completeness...")

    guidelines = _build_guidelines_content("zh")
    standard_tags = guidelines["guidelines"]["tag_standards"]["standard_tags"]

    # 验证必需的标准标签
    required_tags = ["standard", "urgent", "bug", "feature", "refactor",
                     "docs", "test", "api", "frontend", "backend",
                     "database", "security", "performance"]

    for tag in required_tags:
        assert tag in standard_tags, f"Missing required tag: {tag}"

    print("✅ Tag standards completeness test passed!")
    return True


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("Running Guidelines Interface Tests")
    print("=" * 60)
    print()

    tests = [
        test_chinese_guidelines,
        test_english_guidelines,
        test_guidelines_content_builder,
        test_json_serialization,
        test_tag_standards_completeness,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"❌ Test error: {e}")
            print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
