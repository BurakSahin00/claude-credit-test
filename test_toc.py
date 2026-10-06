import toc


def test_nested_output():
    md = "# A\n## B\n### C\n## D\n# E\n"
    assert toc.build_toc(md) == (
        "- [A](#a)\n"
        "  - [B](#b)\n"
        "    - [C](#c)\n"
        "  - [D](#d)\n"
        "- [E](#e)"
    )


def test_ignores_hashes_in_backtick_fence():
    md = "# Real\n```python\n# comment\n## not heading\n```\n## After\n"
    assert [t for _, t in toc.extract_headings(md)] == ["Real", "After"]


def test_ignores_hashes_in_tilde_fence():
    md = "~~~\n# nope\n~~~\n# Yes\n"
    assert toc.extract_headings(md) == [(1, "Yes")]


def test_deeper_levels_and_non_headings_ignored():
    md = "#### Too deep\n#NoSpace\n####### x\n# Ok\n"
    assert toc.extract_headings(md) == [(1, "Ok")]


def test_duplicate_titles_get_unique_anchors():
    out = toc.build_toc("# Intro\n# Intro\n")
    assert "(#intro)" in out and "(#intro-1)" in out


def test_skipped_level_still_nests_one_step():
    assert toc.build_toc("# A\n### C\n") == "- [A](#a)\n  - [C](#c)"


def test_trailing_hashes_stripped():
    assert toc.extract_headings("## Title ##\n") == [(2, "Title")]


def test_cli(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("# Hi\n## There\n", encoding="utf-8")
    assert toc.main([str(f)]) == 0
    assert capsys.readouterr().out == "- [Hi](#hi)\n  - [There](#there)\n"


def test_cli_errors(tmp_path, capsys):
    assert toc.main([]) == 2
    assert toc.main([str(tmp_path / "missing.md")]) == 1
