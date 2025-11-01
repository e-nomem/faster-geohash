use std::error::Error;
use std::fmt::Display;
use std::fmt::Error as FmtError;
use std::fmt::Formatter;

use geohash::GeohashError;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pymodule(gil_used = false)]
mod fast_geohash {
    use std::cmp;

    use geohash::Coord;
    use pyo3::prelude::*;

    use super::FastGeohashError;

    type CoordTuple = (f64, f64);

    #[pyfunction]
    #[pyo3(signature = (coords, /, precision = 12))]
    fn encode(
        py: Python<'_>,
        coords: CoordTuple,
        precision: usize,
    ) -> Result<String, FastGeohashError> {
        py.detach(move || {
            let c = Coord {
                x: coords.0,
                y: coords.1,
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
            let min = (bbox.min().x, bbox.min().y);
            let max = (bbox.max().x, bbox.max().y);
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
            Ok(((x, y), lng_err, lat_err))
        })
    }

    #[pyfunction]
    fn decode(py: Python<'_>, hash_str: &str) -> Result<(String, String), FastGeohashError> {
        py.detach(move || {
            let (coord, lng_err, lat_err) = geohash::decode(hash_str)?;

            let lng_precision = cmp::max((-(lng_err.log10())).round() as i64, 1) - 1;
            let lat_precision = cmp::max((-(lat_err.log10())).round() as i64, 1) - 1;

            let lng = format!("{:.*}", lng_precision as usize, coord.x);
            let lat = format!("{:.*}", lat_precision as usize, coord.y);

            Ok((lng, lat))
        })
    }
}

#[derive(Debug)]
enum FastGeohashError {
    InternalGeohashError(GeohashError),
}

impl Display for FastGeohashError {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result<(), FmtError> {
        match self {
            Self::InternalGeohashError(e) => write!(f, "internal geohash error: {e}"),
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
            FastGeohashError::InternalGeohashError(e) => PyValueError::new_err(format!("{e}")),
        }
    }
}

impl From<GeohashError> for FastGeohashError {
    fn from(value: GeohashError) -> Self {
        Self::InternalGeohashError(value)
    }
}
