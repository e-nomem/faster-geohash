// SPDX-FileCopyrightText: © 2025 Eashwar Ranganathan <eashwar@eashwar.com>
// SPDX-License-Identifier: MIT

use std::cmp;
use std::error::Error;
use std::fmt::Display;
use std::fmt::Error as FmtError;
use std::fmt::Formatter;

use geohash::GeohashError;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pymodule(gil_used = false)]
mod faster_geohash {
    use geohash::Coord;
    use pyo3::prelude::*;

    use super::FastGeohashError;
    use super::error_to_precision;
    use super::format_to_precision;

    type CoordTuple = (f64, f64);

    #[allow(non_upper_case_globals)]
    #[pymodule_export]
    const __version__: &str = env!("CARGO_PKG_VERSION");

    #[pyfunction]
    #[pyo3(signature = (coords, /, precision = 12))]
    fn encode(
        py: Python<'_>,
        coords: CoordTuple,
        precision: usize,
    ) -> Result<String, FastGeohashError> {
        py.detach(move || {
            let c = Coord {
                x: coords.1,
                y: coords.0,
            };
            let result = geohash::encode(c, precision)?;
            Ok(result)
        })
    }

    #[pyfunction]
    fn decode_bbox(
        py: Python<'_>,
        hash_str: &str,
    ) -> Result<(CoordTuple, CoordTuple), FastGeohashError> {
        py.detach(move || {
            let bbox = geohash::decode_bbox(hash_str)?;
            let min = (bbox.min().y, bbox.min().x);
            let max = (bbox.max().y, bbox.max().x);
            Ok((min, max))
        })
    }

    #[pyfunction]
    fn decode_exact(
        py: Python<'_>,
        hash_str: &str,
    ) -> Result<(CoordTuple, f64, f64), FastGeohashError> {
        py.detach(move || {
            let (Coord { x, y }, lng_err, lat_err) = geohash::decode(hash_str)?;
            Ok(((y, x), lat_err, lng_err))
        })
    }

    #[pyfunction]
    fn decode(py: Python<'_>, hash_str: &str) -> Result<(String, String), FastGeohashError> {
        py.detach(move || {
            let (coord, lng_err, lat_err) = geohash::decode(hash_str)?;

            let lng_precision = error_to_precision(lng_err);
            let lat_precision = error_to_precision(lat_err);

            let lng = format_to_precision(coord.x, lng_precision as usize);
            let lat = format_to_precision(coord.y, lat_precision as usize);

            Ok((lat, lng))
        })
    }
}

fn error_to_precision(error: f64) -> i64 {
    let v = error.log10();
    let v = (-v).round();
    cmp::max(v as i64, 1) - 1
}

fn format_to_precision(value: f64, precision: usize) -> String {
    let v = format!("{:.*}", precision, value);
    v.trim_end_matches("0").trim_end_matches(".").into()
}

#[derive(Debug)]
enum FastGeohashError {
    InternalGeohashError(GeohashError),
}

impl Display for FastGeohashError {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result<(), FmtError> {
        match self {
            Self::InternalGeohashError(_) => write!(f, "internal geohash error"),
        }
    }
}

impl Error for FastGeohashError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::InternalGeohashError(e) => Some(e),
        }
    }
}

impl From<FastGeohashError> for PyErr {
    fn from(value: FastGeohashError) -> Self {
        match value {
            FastGeohashError::InternalGeohashError(e) => match e {
                GeohashError::InvalidCoordinateRange(c) => {
                    // Special case for this error because we expect everything in
                    // lat, lng order, but the coords are in the opposite x, y order
                    // So we reformat the error here to avoid confusion
                    PyValueError::new_err(format!(
                        "invalid coordinate range: COORD(lat={}, lng={})",
                        c.y, c.x
                    ))
                }
                e => PyValueError::new_err(format!("{e}")),
            },
        }
    }
}

impl From<GeohashError> for FastGeohashError {
    fn from(value: GeohashError) -> Self {
        Self::InternalGeohashError(value)
    }
}
