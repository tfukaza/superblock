from ntpath import join
from pprint import pprint
from tkinter.tix import TEXT
import requests
import numpy as np
from collections import Counter
import hashlib

from util import *


class Element:
    def __init__(self, ctx=None):
        """
        All Elements contain the following attributes:
        - ctx: Configurations specified by the user
        - info: A dictionary containing information about the element
        """
        self.ctx = ctx
        """
        The info dictionary contains the following information:
        - e_class: A list of classes the user assigned to the element.
        - e_tag: The tag of the element, indicating the type of element.
        - e_main_type: (For group elements) indicates the most common type of element in the group.
        - e_type: Indicates the specific classification of element. E.g. <p> is P
        """
        self.info = {
            "e_class": [],
            "e_tag": None,
            "e_main_type": None,
            "e_type": None,
        }
        """
        The concept of size is very important, as it is used in many crucial algorithms.
        The following chart explains what each size means:
        - 1: Icon - No more than few dozen pixels
        - 2: Small - Width is ~1/4 of current env 
        - 3: Medium - Width is ~1/2 of current env
        - 4: Large - Width spans the entire width of current env

        Sizes in SB are measured in units of rems, where 1 rem = 16px.
        """

    @property
    def e_class(self):
        return self.info["e_class"]

    @e_class.setter
    def e_class(self, value: list):
        self.info["e_class"] = value

    @property
    def e_tag(self):
        return self.info["e_tag"]

    @e_tag.setter
    def e_tag(self, value: str):
        self.info["e_tag"] = value

    @property
    def e_type(self):
        return self.info["e_type"]

    @property
    def e_main_type(self):
        return self.info["e_main_type"]

    def __str__(self) -> str:
        raise NotImplementedError

    def get_size(self, env):
        raise NotImplementedError

    def get_width(self, env):
        raise NotImplementedError

    def get_height(self, env):
        raise NotImplementedError

    # @property
    # def size(self):
    #     return self.get_size()

    # @property
    # def width(self):
    #     return self.get_width()

    # @property
    # def height(self):
    #     return self.get_height()

    def analyze(self):
        # self.info.update(
        #     {
        #         "size": self.get_size(env),
        #         "width": self.get_width(env),
        #         "height": self.get_height(env),
        #     }
        # )
        self.info.update(self.analyze_specific())
        return self.info

    def analyze_specific(self):
        return {}

    def get_info(self):
        return self.info

    def update_info(self, info):
        self.info.update(info)


class ElementDivider(Element):
    def __str__(self) -> str:
        return "<hr>"

    def get_size(self, env):
        return 0

    def get_width(self, env):
        return 0

    def get_height(self, env):
        return 0

    def get_struct_hash(self, depth=-1):
        return ""

    def analyze_specific(self):
        return {
            "e_main_type": e_type.DIVIDER,
            "e_type": e_type.DIVIDER,
        }

class E_VerticalDivider(Element):
    def __str__(self) -> str:
        return "<vr>"

    def get_size(self, env):
        return 0

    def get_width(self, env):
        return 0

    def get_height(self, env):
        return 0

    def get_struct_hash(self, depth=-1):
        return ""

    def analyze_specific(self):
        return {
            "e_main_type": e_type.DIVIDER,
            "e_type": e_type.DIVIDER,
        }


class ElementBaseText(Element):
    def __init__(self, ctx=None):
        super().__init__(ctx)
        self.text = ""
        self.font_size = 1.5  # Default size is 16px and line height is 1.5 (24px)
        self.font_width = 1.0

    def get_width(self, env):
        return len(self.text) * self.font_width

    def get_height(self, env):
        return self.font_size


class ElementHeader(ElementBaseText):
    def __init__(self, ctx, text="", level=1, font_size=2):
        super().__init__(ctx)

        self.text = text
        self.level = level

        size = ((6 - level + 1) / 6) ** 3 + 1.0
        self.font_size = size

    def analyze_specific(self):
        return {
            "e_main_type": e_type.HEADER,
            "e_type": e_type.HEADER,
        }

    def __str__(self) -> str:
        return f"<h{self.level}>{self.text}</h{self.level}>\n"

    def get_size(self, env):
        w1 = 1.0
        return self.get_width(env) * self.get_height(env) * w1

    def get_struct_hash(self, depth=-1):
        text = f"<h{self.level}></h{self.level}>\n"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementParagraph(ElementBaseText):
    def __init__(self, ctx, texts=None, font_size=1.5):
        super().__init__(ctx)
        self.texts = texts

        self.font_size = font_size

    def analyze_specific(self):
        return {
            "e_main_type": e_type.PARAGRAPH,
            "e_type": e_type.PARAGRAPH,
        }

    def __str__(self) -> str:
        if len(self.texts) == 0:
            return ""
        elif len(self.texts) == 1:
            return f"<p>{self.texts[0][1]}</p>"
        else:
            output = []
            for text in self.texts:
                if text[0] == "p":
                    output.append(text[1])
                elif text[0] == "em":
                    output.append(f"<strong>{text[1]}</strong>")
                else:
                    raise NotImplementedError(f"{text[0]}")
            return f"<p>{' '.join(output)}</p>"

    def get_str(self):
        return "".join(t[1] for t in self.texts)

    def get_size(self, env):
        w1 = 1.0
        return self.get_height(env) * self.get_width(env) * w1

    def get_width(self, env):
        l = max(len(t[1]) for t in self.texts)
        return l * self.font_width

    def get_struct_hash(self, depth=-1):
        text = "<p></p>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementLink(ElementBaseText):
    def __init__(self, ctx, text="", font_size=1, href=""):
        super().__init__(ctx)
        self.text = text
        self.font_size = font_size
        self.href = href

    def analyze_specific(self):
        return {
            "e_main_type": e_type.LINK,
            "e_type": e_type.LINK,
        }

    def __str__(self) -> str:
        return f'<a href="{self.href}">{self.text}</a>'

    def get_size(self, env):
        w1 = 1.0
        return self.get_height(env) * self.get_width(env) * w1

    def get_struct_hash(self, depth=-1):
        text = "<a></a>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementSpan(ElementBaseText):
    def __init__(self, ctx, text="", font_size=1):
        super().__init__(ctx)
        self.text = text
        self.font_size = font_size

    def analyze_specific(self):
        return {
            "e_main_type": e_type.SPAN,
            "e_type": e_type.SPAN,
        }

    def __str__(self) -> str:
        return f"<span>{self.text}</span>"

    def get_size(self, env):
        w1 = 1.0
        return self.get_height(env) * self.get_width(env) * w1

    def get_struct_hash(self, depth=-1):
        text = "<span></span>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementButton(ElementBaseText):
    def __init__(self, ctx, text="", font_size=1, href=""):
        super().__init__(ctx)
        self.text = text
        self.font_size = font_size
        self.href = href

    def analyze_specific(self):
        return {
            "e_main_type": e_type.BUTTON,
            "e_type": e_type.BUTTON,
        }

    def __str__(self) -> str:
        return f'<a href="{self.href}">{self.text}</a>'

    def get_size(self, env):
        w1 = 1.0
        return self.get_height(env) * self.get_width(env) * w1

    def get_struct_hash(self, depth=-1):
        text = "<button></button>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementBaseImage(Element):
    def analyze_specific(self):
        return {
            "e_main_type": e_type.IMAGE,
            "e_type": e_type.IMAGE,
            "aspect_ratio": self.aspect_ratio,
        }

    def get_ctx_size(self):
        if self.ctx and "size" in self.ctx:
            size = int(self.ctx["size"])
        else:
            self.ctx["size"] = size = 4
        return size

    def get_size(self, env):
        w1 = 1.0
        return self.get_width(env) * self.get_height(env) * w1

    def get_width(self, env):
        size = self.get_ctx_size()
        if size == 0:
            return 2.0
        elif size == 1:
            return 4.0
        elif size == 2:
            w = 0.25
        elif size == 3:
            w = 0.5
        elif size == 4:
            w = 1.0
        else:
            raise NotImplementedError(f"{size}")
        return env["div_width"] * w

    def get_height(self, env):
        w = self.get_width(env)
        return w * self.aspect_ratio

    def get_struct_hash(self, depth=-1):
        text = "<img>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()


class ElementImage(ElementBaseImage):
    def __init__(self, ctx, url=""):
        super().__init__(ctx)
        if url[:3] == "sb:":
            sizes, keyword = url[3:].split("?")
            h, w = sizes.split("x")
            self.height = int(h)
            self.width = int(w)
            self.channel = 3
            self.url = f"https://source.unsplash.com/random/{self.width}x{self.height}?{keyword}"
        elif url.startswith("ionic"):
            # https://raw.githubusercontent.com/ionic-team/ionicons/main/src/svg/exit.svg
            self.height = 24
            self.width = 24
            self.channel = 3
            self.url = f"https://raw.githubusercontent.com/ionic-team/ionicons/main/src/svg/{url[6:]}.svg"
        else:
            self.url = url
            self.cached = ImageCache("img")
            tup = self.cached.load(url)
            self.height, self.width, self.channel = tup

        self.aspect_ratio = self.height / self.width

    def __str__(self) -> str:
        return f'<img src="{self.url}">'


class ElementImageLink(ElementImage):
    def __str__(self) -> str:
        return f'<a href="{self.href}"><img src="{self.url}"></a>'


class ElementVideo(ElementBaseImage):
    def __init__(self, ctx, url=""):
        super().__init__(ctx)
        self.url = url
        self.cached = ImageCache("img")
        # tup = self.cached.load(url)
        self.height, self.width, self.channel = 1080, 1920, 3
        self.aspect_ratio = self.height / self.width

    def __str__(self) -> str:
        return f'<video src="{self.url}"></video>'


class ElementBaseGroup(Element):
    def __init__(self, ctx=None):
        super().__init__(ctx)
        self.info_cache = None

    def add_element(self, element):
        self.elements.append(element)

    def analyze_specific(self):
        [x.analyze() for x in self.elements]

        # sizes = [x["size"] for x in sub_info]
        types = [x.e_main_type for x in self.elements]
        freq_type = Counter(types).most_common(1)
        freq_type = freq_type[0][0]

        # total_size = sum(sizes)
        # avg_size = total_size / len(sizes)
        # variance = sum(map(lambda x: ((x - avg_size) ** 2) ** 0.5, sizes)) / len(sizes)

        # info = {
        #     "size": total_size,
        #     "avg_size": avg_size,
        #     "variance": variance,
        # }
        info = {
            "e_main_type": freq_type,
        }
        info.update(self.analyze_group_specific())
        # Print the name of this class and the info
        # print(self.__class__.__name__, info)
        return info

    def get_size(self, env):
        return sum(x.get_size(env) for x in self.elements)

    def get_sizes(self, env):
        return [x.get_size(env) for x in self.elements]

    def get_width(self, env):
        return sum(x.get_width(env) for x in self.elements)

    def get_height(self, env):
        return sum(x.get_height(env) for x in self.elements)

    def get_struct_hash(self, depth=-1):
        depth -= 1
        if depth == 0:
            hashes = "" 
        else:
            hashes = [e.get_struct_hash() for e in self.elements]
            hashes = ''.join(hashes)
        text = f"<div>{hashes}</div>"
        hasher = hashlib.sha256()
        hasher.update(text.encode())
        return hasher.hexdigest()

    def get_info(self):
        info = self.info
        child_info = [x.get_info() for x in self.elements]
        info["children"] = child_info
        return info

    def update_info(self, info):
        self.info.update(info)
        assert len(self.elements) == len(info.get("children", 0))
        for i, e in zip(info["children"], self.elements):
            e.update_info(i)


class ElementList(ElementBaseGroup):
    """
    ElementList is a group of ordered elements.
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.elements = []

    def analyze_group_specific(self):
        return {
            "e_type": e_type.LIST,
        }

    def __str__(self) -> str:
        strs = "\n".join(map(lambda x: f"<li>{x}</li>", self.elements))
        return f"<ul>{strs}</ul>"


class ElementGroup(ElementBaseGroup):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.elements = []

    def analyze_group_specific(self):
        return {
            "e_type": e_type.GROUP,
        }

    def __str__(self) -> str:
        if len(self.elements) == 1:
            strs = self.elements[0].__str__()
        else:
            strs = "".join(str(x) for x in self.elements)
        tag = self.e_tag or "div"
        cls = f'class="{self.e_class}"' if self.e_class else ""
        return f"<{tag} {cls}>\n{strs}</{tag}>\n"

    def add_elements(self, elements):
        self.elements.extend(elements)


# class ElementBody(ElementGroup):
#     def analyze(self):
#         return super().analyze(env)
