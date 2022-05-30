import logging
from pprint import pprint
import os
from tkinter import N
import requests
import cv2
import numpy as np
import pickle
import hashlib
import math
import threading
import copy


def trim_text(text, max_len=20):
    return text if len(text) <= max_len else f"{text[:max_len]}..."


def render_m_html(m, tag, content, href=None, src=None, custom=None):
    c = m.class_list_str
    i = f"sb-{m.param['m_id']}-{m.__class__.__name__}"
    d = f'data-x="{m.env["x_current"]}" data-y="{m.env["y_current"]}"'
    href = f'href="{href}"' if href is not None else ""
    src = f'src="{src}"' if src is not None else ""
    score = f'data-score="{m.score()}"' 
    return f"<{tag} {href} {src} {score} class='{c}' {d} id='{i}' {custom}>{content}</{tag}>"


def render_branch_m_html(m, tag, href=None, src=None, optimize=False, env=None):
    render_mods = [i.render_str() for i in m.modules]
    #print(m , render_mods)
    if optimize and len(render_mods) == 1:
        return render_mods[0]
    render_mods = "".join(render_mods)
    if env is not None:
        custom = f'data-div-width="{env["div_width"]}"'
    else:
        custom = ""
    return render_m_html(m, tag, render_mods, href, src, custom)


class ID_Gen_ThreadSafe:
    def __init__(self):
        self.id = 0
        self.lock = threading.Lock()

    def get_id(self):
        with self.lock:
            self.id += 1
            return self.id


# Enum for the different types of elements
from enum import Enum, auto


class e_type(Enum):
    PARAGRAPH = auto()
    HEADER = auto()
    SPAN = auto()
    LINK = auto()
    DIVIDER = auto()

    IMAGE = auto()
    BUTTON = auto()

    LIST = auto()
    GROUP = auto()

class prof(Enum):
    DEFAULT = auto()
    LANDING = auto()
    INFO = auto()


def img_ctx_size(img):
    return int(img.ctx.get("size", 0))


def filter_scores(scores):
    r = [s for s in scores if s >= 0]
    if len(r) == 0:
        return -1
    return sum(r) / len(r)


def is_element_group(e):
    return e.e_type in [e_type.GROUP, e_type.LIST]


def is_element_text(e, allow_group=False):
    chk = e.e_main_type if allow_group else e.e_type
    return chk in [e_type.PARAGRAPH, e_type.HEADER, e_type.SPAN, e_type.LINK]


def is_element_img(e, size=None):
    if not e.e_type in [e_type.IMAGE]:
        return False
    if size is not None and img_ctx_size(e) != size:
        return False
    return True


def is_module_group(m):
    return m.m_type in [e_type.GROUP, e_type.LIST]


def is_module_text(m):
    return m.m_type in [e_type.PARAGRAPH, e_type.HEADER, e_type.SPAN]


def get_img_size(e):
    return 0 if e.e_tag != "img" else int(e.ctx.get("size", 0))


def get_text_ratio(env, e):
    d_width = env["div_width"]
    p_width = e.get_width(env)
    h = p_width / d_width
    h = h * e.get_height(env)

    return h / d_width


def get_parent_param_by_class(p, cls):
    while p["parent"] is not None:
        if p["parent"].get("class") == cls:
            return p["parent"]
        p = p["parent"]
    return None


def get_parent_param_by_type(p, e_type):
    while p["parent"] is not None:
        if p["parent"].get("e_main_type") == e_type:
            return p["parent"]
        p = p["parent"]
    return None


def is_divider(e, h=2):
    if e.e_tag == "hr":
        return True
    if e.e_tag[0] == "h" and int(e.e_tag[1]) <= h:
        return True

    return False


def is_m_divider(m):
    if m.m_type == e_type.DIVIDER:
        return True
    if m.m_type == e_type.HEADER and int(m.e0.e_tag[1]) <= 2:
        return True

    return False


def flatten_elements(elements, depth=-1):
    if elements.elements is None or depth == 0:
        return [elements]

    flat_elements = []
    for e in elements:
        if e.elements is not None:
            flat_elements.extend(flatten_modules(e, depth - 1))
        else:
            flat_elements.append(e)
    return flat_elements

def flatten_modules(module, depth=-1):
    if module.modules is None or depth == 0:
        return [module]

    flat_modules = []
    for m in module.modules:
        if m.modules is not None:
            flat_modules.extend(flatten_modules(m, depth - 1))
        else:
            flat_modules.append(m)
    return flat_modules


def flatten_modules_list(modules, depth=-1):
    if depth == 0:
        return modules

    flat_modules = []
    for m in modules:
        if m.modules is not None:
            flat_modules.extend(flatten_modules_list(m.modules, depth - 1))
        else:
            flat_modules.append(m)
    return flat_modules


class ImageCache:
    """
    Users can call the "load" function to load an image based on a url.
    If the url is saved locally in the "img" directory, load the image.
    If not, fetch the image from the url and save it locally.

    Image should be opened in as a OpenCV2 image.
    """

    def __init__(self, img_dir):
        self.img_dir = img_dir
        self.cache = {}

    def load(self, url):

        # Use SHA256 to hash the url
        hasher = hashlib.sha256()
        hasher.update(url.encode())
        url_hash = hasher.hexdigest()

        if url_hash in self.cache:
            return self.cache[url_hash][0]

        img_path = self.img_dir + "/" + url_hash
        if os.path.isfile(img_path):
            # Open data saved as pickle
            with open(img_path, "rb") as f:
                tup = pickle.load(f)
        else:
            tup = self.fetch_img(url)
            # Save data as pickle
            with open(img_path, "wb") as f:
                pickle.dump(tup, f)
        self.cache[url_hash] = tup

        return tup[0]

    def fetch_img(self, url):
        url = url.replace("&amp;", "&")
        print(f"Loading image from {url}")
        if "http" in url:
            response = requests.get(url).content
            if "svg" in url:
                # Convert response to string
                response = response.decode("utf-8")
                # Find the "height" and "width" attributes from the svg
                # and convert them to integers
                height_str = response.split('height="')[1].split('"')[0]
                width_str = response.split('width="')[1].split('"')[0]
                height = int(height_str.replace("px", ""))
                width = int(width_str.replace("px", ""))
                # Set the raw height and width
                channels = 3
                # TODO: convert to png
                return ((height, width, channels), None)
            else:
                nparr = np.frombuffer(response, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        else:
            img = cv2.imread(url)
        return (img.shape, img)
    
    def load_img(self, url):
        if "svg" in url:
            return None
        else:
            img = cv2.imread(url)
        if img is None:
            img = self.fetch_img(url)[1]
        return img

def upto_divider(elements):
    i = 0
    while i < len(elements) and not is_divider(elements[i]):
        i += 1
    return i, elements[:i]


def strings_to_classes(strings):
    if strings is None:
        return []
    return [
        getattr(__import__("modules"), m) if isinstance(m, str) else m for m in strings
    ]


def deepcopy_param(p):
    new_p = p.copy()
    new_p["class_list"] = p["class_list"].copy()
    return new_p

standard_widths = {
  #  "1/4": 1 / 4,
    "1/3": 1 / 3,
    "2/5": 2 / 5,
    "1/2": 1 / 2,
    "2/3": 2 / 3,
    "3/4": 3 / 4,
    "4/5": 4 / 5,
    "5/6": 5 / 6,
    "full": 1,
}

def tw_w_to_float(tw_w):
    return standard_widths[tw_w]

def tw_float_to_w(tw_float, granular=False):
    """
    Given a float, return the tailwind CSS width
    that best approximates the float.
    """
    d = {
        1 / 3.: "1/3",
        2 / 5: "2/5",
        1 / 2: "1/2",
        2 / 3: "2/3",
        3 / 4: "3/4",
        4 / 5: "4/5",
        5 / 6: "5/6",
        1: "full",
    }
    if granular:
        d.update({
            1 / 12: "1/12",
            2 / 12: "2/12",
            3 / 12: "3/12",
            4 / 12: "4/12",
            5 / 12: "5/12",
         
            7 / 12: "7/12",
            8 / 12: "8/12",
         
            10 / 12: "10/12",
            11 / 12: "11/12",
        })
    widths = list(d.keys())
    tw_widths = list(d.values())
    diffs = [abs(w - tw_float) for w in widths]
    best_index = diffs.index(min(diffs))
    return tw_widths[best_index]
   
# https://www.geeksforgeeks.org/maximum-size-rectangle-binary-sub-matrix-1s/
def max_hist(hist):
    max_hist = max(hist)
    len_hist = len(hist)
    max_area = 0
    max_x, max_y, max_w = 0, 0, 0
    stack = []
    i = 0
    while i < len_hist:
        # if this bar is higher than the bar on top of stack, push it to stack
        if not stack or hist[stack[-1]] <= hist[i]:
            stack.append(i)
            i += 1
            continue 
    
        # if this bar is lower than the bar on top of stack
        y = hist[stack.pop(-1)]
        x = stack[-1]+1 if stack else 0
        area = y * (i - x)
        if area > max_area:
            max_area = area
            max_y = y
            max_x = x
            max_w = i - x

    while stack:
        y = hist[stack.pop(-1)]
        x = stack[-1]+1 if stack else 0
        area = y * (i - x)
        if area > max_area:
            max_area = area
            max_y = y
            max_x = x
            max_w = i - x
    
    return max_area, max_x, max_y, max_w

# h = [6, 2, 5, 4, 5, 1, 6]
# print(max_hist(h))

def max_rectangle(rect):
    max_area = 0
    max_x, max_y, max_w, max_h = 0, 0, 0, 0
    rows = [rect[0]]
    for y in range(1, len(rect)):
        row = []
        for x in range(len(rect[y])):
            if rect[y][x] != 0:
                row.append(rows[y-1][x]+1)
            else:
                row.append(0)
        area, x, h, w = max_hist(row)
        if area > max_area:
            max_area = area
            max_x = x
            max_y = y-h+1
            max_w = w
            max_h = h

        rows.append(row)
    return max_area, max_x, max_y, max_w, max_h

import itertools

# def analyze_img(url, txt_rgb):
#url="https://img.cdn4dd.com/cdn-cgi/image/fit=cover,width=1200,format=auto,quality=60/https://cdn.doordash.com/media/consumer/home/landing/new/hero_landing_us_alt.jpg"
#url="https://images.unsplash.com/photo-1544984243-ec57ea16fe25?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=987&q=80"
#url="https://a0.muscache.com/im/pictures/6dbfc87a-22a4-4d4a-b352-99aa93a98e78.jpg?im_w=1440"
#url="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=3270&q=80"
#url="https://www.uber-assets.com/image/upload/v1613106985/assets/0e/47aa71-35cb-459a-a975-78c61ea300e2/original/HP-U4B-NYC-bkg.png"
#url="https://a0.muscache.com/im/pictures/cca24f3f-8f66-4e9d-98d8-dd5cda8911eb.jpg?im_w=2560"

def img_max_rect(url, txt_rgb, th_contrast=0.2, th_edge_0 = 0.8, th_edge_1=0.5):
   
    txt_color = sum(txt_rgb) / 3
    PROC_SCALE = 64
    th_contrast = 0.2
    th_edge = th_edge_0
    th_edge_1 = 128 * th_edge_1

    img = ImageCache("img").load_img(url)

    # Remove alpha channel
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    # Grayscale + blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    orig_shape = blur.shape
    orig_size = orig_shape[::-1]
    pix_size = (
        math.ceil(orig_shape[0]/PROC_SCALE), 
        math.ceil(orig_shape[1]/PROC_SCALE))
    pix_size_rev = (pix_size[1], pix_size[0])

    # Edge detection
    edge = cv2.Canny(blur, int(100*th_edge), int(200*th_edge))
    edge_1 = np.zeros(pix_size, dtype=np.uint8)
    for y, x in itertools.product(range(0, edge.shape[0], PROC_SCALE), range(0, edge.shape[1], PROC_SCALE)):
        roi = edge[y:y+PROC_SCALE, x:x+PROC_SCALE]
        num_nonzero = np.count_nonzero(roi)
        v = 255 if num_nonzero > th_edge_1 else 0
        edge_1[y//PROC_SCALE][x//PROC_SCALE] = v
    edge_pix = edge_1.copy()
    edge_1 = cv2.resize(edge_1, orig_size, interpolation=cv2.INTER_NEAREST)

    # Color contrast
    pixelate = cv2.resize(blur, pix_size_rev, interpolation=cv2.INTER_LINEAR)
    for y, x in itertools.product(range(pixelate.shape[0]), range(pixelate.shape[1])):
        pix = pixelate[y][x]
        pixelate[y][x] = 0 if abs(pix - txt_color)/255 > th_contrast else 255
    contrast_pix = pixelate.copy()
    contrast = cv2.resize(pixelate, orig_size, interpolation=cv2.INTER_NEAREST)

    
    cmb_pix = cv2.add(edge_pix, contrast_pix, dtype=cv2.CV_8U)
    cmb_arr = cmb_pix.copy()
    for y in range(cmb_pix.shape[0]):
        for x in range(cmb_pix.shape[1]):
            cmb_arr[y][x] = 0 if cmb_pix[y][x] > 0 else 1
    a, x, y, w, h = max_rectangle(cmb_arr)
    print(a, x, y, w, h)
    
    # empty_pix = np.zeros(pix_size, dtype=np.uint8)
    # cmb_max = empty_pix
    # for i in range(y, y+h):
    #     for j in range(x, x+w):
    #         cmb_max[i][j] = 255
    # cmb_img = cv2.resize(cmb_max, orig_size, interpolation=cv2.INTER_NEAREST)
    # overlay = cv2.cvtColor(cmb_img, cv2.COLOR_GRAY2RGB)
    # overlay = cv2.addWeighted(img, 0.5, overlay, 0.5, 0, dtype=cv2.CV_8U)
    # cv2.imshow("overlay", overlay)
    # cv2.waitKey(0)
    # overlay = cv2.subtract(img, overlay)

    #cv2.destroyAllWindows()
    area = PROC_SCALE * PROC_SCALE * a / 16 / 16
    x_start = x * PROC_SCALE / orig_shape[1]
    y_start = y * PROC_SCALE / orig_shape[0]
    width = w * PROC_SCALE / orig_shape[1]
    height = h * PROC_SCALE / orig_shape[0]

    return area, x_start, y_start, width, height