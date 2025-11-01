import pytest

import fast_geohash


def test_encode_explicit_len() -> None:
	result = fast_geohash.encode((112.5584, 37.8324), precision=9)

	assert result == 'ww8p1r4t8'


def test_encode_default_len() -> None:
	result = fast_geohash.encode((112.5584, 37.8324))

	assert result == 'ww8p1r4t8yd0'


def test_encode__invalid_coordinates() -> None:
	with pytest.raises(ValueError) as e:
		fast_geohash.encode((float('nan'), 37.8324), 9)

	assert str(e.value) == 'invalid coordinate range: COORD(NaN 37.8324)'


def test_encode__invalid_length() -> None:
	with pytest.raises(ValueError) as e:
		fast_geohash.encode((112.5584, 37.8324), 14)

	assert str(e.value) == 'Invalid length specified: 14. Accepted values are between 1 and 12, inclusive'


def test_decode_bbox() -> None:
	assert fast_geohash.decode_bbox('ww8p1r4t8') == (
		(112.55836486816406, 37.83236503601074),
		(112.5584077835083, 37.83240795135498),
	)


def test_decode_exact() -> None:
	assert fast_geohash.decode_exact('ww8p1r4t8') == (
		(112.55838632583618, 37.83238649368286),
		2.1457672119140625e-05,
		2.1457672119140625e-05,
	)


def test_decode() -> None:
	assert fast_geohash.decode('ww8p1r4t8') == ('112.5584', '37.8324')
