from re import M
from util import *
import math


def sigmoid(x, a=1, b=0, c=0):
    # cap x between [-10, 10]
    x = max(min(x, 10), -10)
    return 1 / (1 + math.exp(-a * (x + b))) + c


def score_text_ratio(mod, c_width, a=0.3, b=5, c=2):
    """
    Score the ratio of the text in a given element.
    """
    m_width = mod.get_width(False)
    rows = m_width / c_width
    # print(m_width, c_width, rows)
    height = rows * mod.get_height(False)
    ratio = height / c_width
    diff = a - ratio
    diff = diff * b
    score = diff**c
    score = 1 - (1 / (1 + (1 / score)))
    return score


def score_p_eyetrack(modules, env):
    if len(modules) < 2:
        return -1
    scores = []
    for i in range(1, len(modules)):
        m1 = modules[i]
        m0 = modules[i - 1]
        m0_x1 = m0.env["x_current"] + m0.get_width(True)
        m0_y1 = m0.env["y_current"] + m0.get_height(True)
        m1_x0 = m1.env["x_current"]
        m1_y0 = m1.env["y_current"]
        d = math.sqrt((m1_x0 - m0_x1) ** 2 + (m1_y0 - m0_y1) ** 2)
        d_p = sigmoid(d, a=0.1)
        y_d = m1_y0 - m0_y1
        y_d_p = sigmoid(y_d)
        avg = (d_p + y_d_p) / 2
        scores.append(avg)

    return sum(scores) / len(scores)


def tw_w_to_rem(tw_w, env):
    """
    Takes a width defined by tailwind CSS (e.g. w-44, w-1/2)
    and returns its equivalent in rem.
    """
    if tw_w.endswith("px"):
        return 1 / 16

    c_width = env.get("div_width", 72)

    val = tw_w.split("-")[1]
    if "/" in val:
        val = val.split("/")
        val = float(val[0]) / float(val[1])
        return val * c_width
    elif val == "screen":
        return c_width
    elif val == "full":
        return c_width
    # else if val is all numbers
    elif val.isdigit():
        return int(val) / 4
    else:
        return c_width
