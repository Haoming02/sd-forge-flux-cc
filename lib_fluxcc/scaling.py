from math import cos, sin, pi


def apply_scaling(
    alg: str,
    current_step: int,
    total_steps: int,
    bri: float,
    con: float,
    temp: float,
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    p5: float,
) -> list:

    mod = 1.0

    if alg != "Flat":
        ratio = float(current_step / total_steps)
        rad = ratio * pi / 2

        match alg:
            case "Cos":
                mod = cos(rad)
            case "Sin":
                mod = sin(rad)

    return [
        bri * mod,
        con * mod,
        temp * mod,
        p1 * mod,
        p2 * mod,
        p3 * mod,
        p4 * mod,
        p5 * mod,
    ]
