# fast-geohash
[![PyPI version](https://img.shields.io/pypi/v/fast-geohash.svg)](https://pypi.org/projects/fast-geohash) [![License](https://img.shields.io/github/license/e-nomem/fast-geohash.svg)](https://github.com/e-nomem/fast-geohash/blob/main/LICENSE)

A fast geohash library for python implemented using the [rust geohash crate](https://github.com/georust/geohash).

This library supports python 3.9-3.14 and has experimental support for the 'free-threaded' mode in python 3.14.

## Usage
```python
import fast_geohash

fast_geohash.encode((112.5584, 37.8324), precision=9)  # 'ww8p1r4t8'

fast_geohash.decode('ww8p1r4t8')  # ('112.5584', '37.8324')
```

## Building
This library uses `maturin` to compile the rust code into a python extension module. An existing rust toolchain does not have to be installed because `maturin` will bootstrap a rust toolchain in an isolated environment as necessary. Use any standard build frontend, e.g. using `uv`:
```bash
# Build from source checkout
uv build --wheel .

# Build directly from sdist
uv build --wheel path/to/fast_geohash-0.0.1.tar.gz
```

### ABI3 Support
This library supports building against the python 'limited' API/ABI3. By default it will not do so, but the option can be enabled by passing the config flag to maturin. E.g. using `uv`:
```bash
uv build --config-setting maturin.build-args=--features=abi3 --wheel <source_dir or sdist>
```
