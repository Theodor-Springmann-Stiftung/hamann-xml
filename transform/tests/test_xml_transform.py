from pathlib import Path

from hamann_transform.xml_transform import transform_xml


class RecordingNormalizer:
    def __init__(self, replacements: dict[str, str]) -> None:
        self.replacements = replacements
        self.seen: list[str] = []

    def normalize_many(self, texts: list[str]) -> list[str]:
        self.seen.extend(texts)
        return [self.replacements.get(text, text) for text in texts]


def test_projects_normalization_across_inline_tags(tmp_path: Path) -> None:
    source = tmp_path / "input.xml"
    output = tmp_path / "output.xml"
    original = (
        '<?xml version="1.0" encoding="utf-8"?><opus><document>\n'
        '\t<letterText letter="1">\n'
        '\t\t<line index="1" />Er will es wi<del>ß</del>en und <aq>bey</aq> mir seyn.\n'
        "\t</letterText>\n"
        "</document></opus>\n"
    )
    source.write_text(original, encoding="utf-8")
    normalizer = RecordingNormalizer(
        {"Er will es wißen und bey mir seyn.": "Er will es wissen und bei mir sein."}
    )

    summary = transform_xml(source, output, normalizer)

    assert normalizer.seen == ["Er will es wißen und bey mir seyn."]
    assert "wi<del>ss</del>en" in output.read_text(encoding="utf-8")
    assert "<aq>bei</aq> mir sein" in output.read_text(encoding="utf-8")
    assert summary["changed_segments"] == 1


def test_skipped_tags_are_unchanged_barriers(tmp_path: Path) -> None:
    source = tmp_path / "input.xml"
    output = tmp_path / "output.xml"
    original = (
        '<?xml version="1.0" encoding="utf-8"?><opus><document>'
        '<letterText letter="1"><line />vor<nr>&#x2003;</nr>nach '
        '<gr>λογος</gr> und <hb>אב</hb>.</letterText></document></opus>'
    )
    source.write_text(original, encoding="utf-8")
    normalizer = RecordingNormalizer({})

    transform_xml(source, output, normalizer)

    assert normalizer.seen == ["vor", "nach", "und", "."]
    assert output.read_text(encoding="utf-8") == original


def test_unselected_letters_and_comments_remain_byte_identical(tmp_path: Path) -> None:
    source = tmp_path / "input.xml"
    output = tmp_path / "output.xml"
    original = (
        '<?xml version="1.0" encoding="utf-8"?><opus><document>\n'
        '<!-- keep this -->\n'
        '<letterText letter="1"><line />bey mir</letterText>\n'
        '<letterText letter="2"><line />bey dir</letterText>\n'
        '</document></opus>'
    )
    source.write_text(original, encoding="utf-8")
    normalizer = RecordingNormalizer({"bey mir": "bei mir"})

    transform_xml(source, output, normalizer, letters={"1"})
    result = output.read_text(encoding="utf-8")

    assert "<!-- keep this -->" in result
    assert '<letterText letter="1"><line />bei mir</letterText>' in result
    assert '<letterText letter="2"><line />bey dir</letterText>' in result
