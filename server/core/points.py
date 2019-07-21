import math


def run_stats(distance, time):
    """returns 10 points per km, and 1 point per 2 minutes"""
    x = (distance * 10) / 1000
    y = (time * 1 / 120)
    result = x + y
    return result


def levelcalc(points):
    levelpoints = 0.6 * math.sqrt(points)
    level = math.floor(levelpoints)
    return level

def levelToPoints(level):
    points = math.floor(((level / 0.6) ** 2))
    return points

def calculateLevelProgress(points):
    currentLevel = levelcalc(points)
    currentLevelPoints = levelToPoints(currentLevel)
    nextLevelPoints = levelToPoints(currentLevel + 1)
    level_total = abs(nextLevelPoints - currentLevelPoints)
    level_progress = abs(points - currentLevelPoints)
    progress = level_progress / level_total
    return progress



if __name__ == "__main__":
    result = run_stats(60, 360)
    # hardcoded for now
    points = 0
    points = points + result
    print("You received", result, "points this session!")
    level = levelcalc(points)
    print("You are level", level, "!")
