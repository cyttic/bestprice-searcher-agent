"""Reader for the CSV files produced by il_supermarket_parsers.

The parser's CSV writer compresses repeated consecutive values (across rows
belonging to the same source file) by blanking them out, on the assumption a
downstream reader will forward-fill. It distinguishes a genuinely empty
source value (written as the literal two-character sentinel "''") from a
blanked/repeated cell (written as a truly empty cell). We have to undo both
transformations to get the real values back.
"""

import pandas as pd

_SENTINEL = "''"


def read_parsed_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df.replace("", pd.NA).ffill()
    df = df.replace(_SENTINEL, "")
    return df
