import math


def run_stats(distance, time):
    """returns 10 points per km, and 1 point per minute"""
    x = distance * 10
    y = time * 1
    result = x + y
    return result


def levelcalc(points):
    levelpoints = 0.6 * math.sqrt(points)
    level = math.floor(levelpoints)
    return level


if __name__ == "__main__":
    result = run_stats(60, 360)
    # hardcoded for now
    points = 0
    points = points + result
    print("You received", result, "points this session!")
    level = levelcalc(points)
    print("You are level", level, "!")
