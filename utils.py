def availability_to_int(a: list[str]) -> int:
    availability = 0
    for i in range(7):
        for j in range(3):
            if f"{i}-{j}" in a:
                availability += 2 ** (i * 3 + j)
    return availability


def availability_to_list(a: int) -> list[str]:
    availability = []
    for i in range(7):
        for j in range(3):
            if a & (1 << (i * 3 + j)) != 0:
                availability.append(f"{i}-{j}")
    return availability
