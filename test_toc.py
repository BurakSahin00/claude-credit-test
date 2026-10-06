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


# --max-depth

def test_max_depth_limits_levels():
    md = "# A\n## B\n### C\n## D\n"
    assert toc.build_toc(md, max_depth=2) == "- [A](#a)\n  - [B](#b)\n  - [D](#d)"
    assert toc.build_toc(md, max_depth=1) == "- [A](#a)"


def test_max_depth_keeps_anchors_of_duplicates_stable():
    md = "# Intro\n## Intro\n"
    assert toc.build_toc(md, max_depth=1) == "- [Intro](#intro)"
    assert toc.build_toc("## Intro\n# Intro\n", max_depth=1) == "- [Intro](#intro-1)"


def test_cli_max_depth(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("# A\n## B\n", encoding="utf-8")
    assert toc.main([str(f), "--max-depth", "1"]) == 0
    assert capsys.readouterr().out == "- [A](#a)\n"


def test_cli_max_depth_invalid(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("# A\n", encoding="utf-8")
    assert toc.main([str(f), "--max-depth", "0"]) == 2
    assert toc.main([str(f), "--max-depth", "abc"]) == 2


# --output

def test_cli_output_writes_file(tmp_path, capsys):
    f = tmp_path / "x.md"
    out = tmp_path / "toc.md"
    f.write_text("# Hi\n## There\n", encoding="utf-8")
    assert toc.main([str(f), "--output", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == "- [Hi](#hi)\n  - [There](#there)\n"
    assert capsys.readouterr().out == ""


def test_cli_output_unwritable(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("# Hi\n", encoding="utf-8")
    assert toc.main([str(f), "--output", str(tmp_path / "no" / "dir.md")]) == 1
    assert "Error" in capsys.readouterr().err


# --numbered

def test_numbered_restarts_under_each_parent():
    md = "# A\n## B\n## C\n# D\n## E\n"
    assert toc.build_toc(md, numbered=True) == (
        "1. [A](#a)\n"
        "   1. [B](#b)\n"
        "   2. [C](#c)\n"
        "2. [D](#d)\n"
        "   1. [E](#e)"
    )


def test_numbered_with_max_depth():
    md = "# A\n## B\n### C\n# D\n"
    assert toc.build_toc(md, max_depth=2, numbered=True) == (
        "1. [A](#a)\n   1. [B](#b)\n2. [D](#d)"
    )


def test_cli_numbered(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("# A\n# B\n", encoding="utf-8")
    assert toc.main([str(f), "--numbered"]) == 0
    assert capsys.readouterr().out == "1. [A](#a)\n2. [B](#b)\n"
