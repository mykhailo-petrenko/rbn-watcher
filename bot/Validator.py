import re

CALL_FILTER_REGEX = re.compile(r"^[A-Z0-9/]{3,15}$")

def validate_callsign_filter(call_filter: str):
    m = CALL_FILTER_REGEX.match(call_filter)
    return m is not None


if __name__ == "__main__":
    assert validate_callsign_filter("UR3AMP") == True
    assert validate_callsign_filter("UR3AMP09//adasd") == False
