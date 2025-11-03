# SPDX-License-Identifier: MIT
import pytest

import faster_geohash


def test_encode_explicit_len() -> None:
	result = faster_geohash.encode((37.8324, 112.5584), precision=9)

	assert result == 'ww8p1r4t8'


def test_encode_default_len() -> None:
	result = faster_geohash.encode((37.8324, 112.5584))

	assert result == 'ww8p1r4t8yd0'


def test_encode__invalid_coordinates() -> None:
	with pytest.raises(ValueError) as e:
		faster_geohash.encode((float('nan'), 112.5584), 9)

	assert str(e.value) == 'invalid coordinate range: COORD(lat=NaN, lng=112.5584)'


def test_encode__invalid_length() -> None:
	with pytest.raises(ValueError) as e:
		faster_geohash.encode((37.8324, 112.5584), 14)

	assert str(e.value) == 'Invalid length specified: 14. Accepted values are between 1 and 12, inclusive'


def test_decode_bbox() -> None:
	assert faster_geohash.decode_bbox('ww8p1r4t8') == (
		(37.83236503601074, 112.55836486816406),
		(37.83240795135498, 112.5584077835083),
	)


def test_decode_exact() -> None:
	assert faster_geohash.decode_exact('ww8p1r4t8') == (
		(37.83238649368286, 112.55838632583618),
		2.1457672119140625e-05,
		2.1457672119140625e-05,
	)


def test_decode() -> None:
	assert faster_geohash.decode('ww8p1r4t8') == ('37.8324', '112.5584')


def test_round_trip() -> None:
	coord = (37, 112)
	geohash = faster_geohash.encode(coord, precision=12)
	decoded = faster_geohash.decode(geohash)

	assert decoded == tuple(str(v) for v in coord)
