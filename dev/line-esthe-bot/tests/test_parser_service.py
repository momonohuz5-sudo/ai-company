from app.services.parser_service import ParseStatus, parse_query


def test_space_separated():
    result = parse_query("ABC新宿 あい")
    assert result.status == ParseStatus.OK
    assert result.query.shop_name == "ABC新宿"
    assert result.query.therapist_name == "あい"


def test_newline_separated():
    result = parse_query("ABC新宿\nあい")
    assert result.status == ParseStatus.OK
    assert result.query.shop_name == "ABC新宿"
    assert result.query.therapist_name == "あい"


def test_no_particle_separated():
    result = parse_query("ABC新宿のあい")
    assert result.status == ParseStatus.OK
    assert result.query.shop_name == "ABC新宿"
    assert result.query.therapist_name == "あい"


def test_single_name_missing_shop():
    result = parse_query("あい")
    assert result.status == ParseStatus.MISSING_SHOP


def test_empty_text_unparseable():
    result = parse_query("   ")
    assert result.status == ParseStatus.UNPARSEABLE
