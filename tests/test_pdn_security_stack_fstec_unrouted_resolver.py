from TOOLS.pdn_security_stack_resolve_fstec_unrouted_attachments import candidate_attachment_links, extract_landing, mime_for


def test_resolves_single_same_host_pdf_attachment():
    landing = "https://fstec.ru/dokumenty/vse-dokumenty/perechni/example"
    html = '<a href="/files/abc/test.pdf">PDF</a>'
    assert candidate_attachment_links(html, landing) == ["https://fstec.ru/files/abc/test.pdf"]


def test_rejects_off_site_and_non_files_links():
    landing = "https://fstec.ru/dokumenty/vse-dokumenty/perechni/example"
    html = (
        '<a href="https://evil.example/files/test.pdf">bad</a>'
        '<a href="/download/test.pdf">not files</a>'
        '<a href="/files/abc/test.txt">wrong type</a>'
    )
    assert candidate_attachment_links(html, landing) == []


def test_multiple_plausible_attachments_remain_ambiguous_for_caller():
    landing = "https://fstec.ru/dokumenty/vse-dokumenty/perechni/example"
    html = '<a href="/files/a.pdf">A</a><a href="/files/b.pdf">B</a>'
    assert candidate_attachment_links(html, landing) == [
        "https://fstec.ru/files/a.pdf",
        "https://fstec.ru/files/b.pdf",
    ]


def test_duplicate_attachment_is_deduplicated():
    landing = "https://fstec.ru/dokumenty/example"
    html = '<a href="/files/a.pdf">A</a><a href="/files/a.pdf">A again</a>'
    assert candidate_attachment_links(html, landing) == ["https://fstec.ru/files/a.pdf"]


def test_landing_must_be_explicitly_registered():
    assert extract_landing('canonical_source:\n  landing_page: "https://fstec.ru/x"\n') == "https://fstec.ru/x"
    assert extract_landing("canonical_source:\n  publisher: FSTEC\n") is None


def test_supported_mime_is_derived_from_route_only():
    assert mime_for("https://fstec.ru/files/a.pdf") == "application/pdf"
    assert mime_for("https://fstec.ru/files/a.doc") == "application/msword"
    assert mime_for("https://fstec.ru/files/a.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
