def encode(coords: tuple[float, float], /, precision: int = 12) -> str:
	"""Encodes a coordinate point into a geohash

	:param coords: A coordinate tuple of (longitude, latitude)
	:type coords: tuple[float, float]
	:param precision: The precisions/length of the output geohash from
		1 to 12 inclusive (defaults to 12)
	:type precision: int
	:returns: The coordinate encoded as a geohash string
	:rtype: str
	"""
	...

def decode_bbox(hash_str: str) -> tuple[tuple[float, float], tuple[float, float]]:
	"""Decode a geohash returning the bounding box that contains it

	:param hash_str: The geohash string
	:type hash_str: str
	:returns: The bounding box as a (min_coord, max_coord) tuple where
		each coord is a tuple of (longitude, latitude)
	:rtype: tuple[tuple[float, float], tuple[float, float]]
	"""
	...

def decode_exact(hash_str: str) -> tuple[tuple[float, float], float, float]:
	"""Decode a geohash returning a coordinate and error margins

	:param hash_str: The geohash string
	:type hash_str: str
	:returns: A tuple of (coordinate, longitude_error, latitude_error) where
		the coordinate is a tuple of (longitude, latitued) and each error value
		is a float
	:rtype: tuple[tuple[float, float], float, float]
	"""
	...

def decode(hash_str: str) -> tuple[str, str]:
	"""Decode a geohash returning a coordinate with truncated precision

	:param hash_str: The geohash string
	:type hash_str: str
	:returns: The coordinate as a tuple of strings (longitude, latitude)
		with each string represnentation truncated to a precision matching
		the error margins
	:rtype: tuple[str, str]
	"""
	...
