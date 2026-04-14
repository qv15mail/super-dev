from super_dev.seeai_design_system import (
    SEEAI_EXECUTION_GUARDRAILS,
    SEEAI_FAILURE_PROTOCOL,
    SEEAI_JUDGE_CHECKLIST,
    SEEAI_MODULE_TRUTH_RULES,
    SEEAI_QUALITY_FLOOR,
    get_seeai_archetype_playbook_map,
    get_seeai_design_pack_map,
)


def test_design_packs_capture_competition_ui_direction():
    packs = get_seeai_design_pack_map()

    assert set(packs) == {"arena_neon", "clean_product", "playful_motion"}
    assert "紫粉渐变" in packs["arena_neon"]["color_story"]
    assert "默认 SaaS 模板" not in packs["clean_product"]["guardrail"]
    assert "主循环" in packs["playful_motion"]["guardrail"]


def test_archetype_playbooks_expose_runtime_checkpoint_and_fallback_stack():
    playbooks = get_seeai_archetype_playbook_map()

    assert "12 分钟内" in playbooks["landing_page"]["runtime_checkpoint"]
    assert "HTML + Tailwind CDN + GSAP" in playbooks["landing_page"]["fallback_stack"]
    assert "Canvas" in playbooks["mini_game"]["fallback_stack"]
    assert "mock 数据" in playbooks["tool"]["fallback_stack"]


def test_quality_and_failure_guardrails_prioritize_demo_reliability():
    assert any("12 分钟内必须跑出第一个可见" in item for item in SEEAI_EXECUTION_GUARDRAILS)
    assert any("初始化失败一次后" in item for item in SEEAI_FAILURE_PROTOCOL)
    assert any("3 秒内必须让评委看懂" in item for item in SEEAI_QUALITY_FLOOR)
    assert any("30 秒主演示路径" in item for item in SEEAI_JUDGE_CHECKLIST)
    assert any("真实启动" in item for item in SEEAI_MODULE_TRUTH_RULES)
