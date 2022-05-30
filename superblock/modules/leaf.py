from elements import *
from modules.base import *
from score import *

# from modules.group import *
import math


class M_Divider(LeafModule):
    def match(elements, param, save, env):
        if len(elements) == 0:
            return -1, 0
        if elements[0].e_tag == "hr":
            return 1, 1
        return -1, 0

    def render_str(self):
        return ""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class M_VerticalDivider(LeafModule):
    def match(elements, param, save, env):
        if len(elements) == 0:
            return -1, 0
        if elements[0].e_tag == "vr":
            return 1, 1
        return -1, 0

    def render_str(self):
        return ""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class M_Header(LeafModule):

    normal = {
        1: "text-4xl",
        2: "text-xl",
        3: "text-xl",
        4: "text-lg",
        5: "text-lg",
        6: "text-md",
    }
    compact = {
        1: "text-xl",
        2: "text-lg",
        3: "text-lg",
        4: "text-md",
        5: "text-md",
        6: "text-md",
    }

    def match(elements, param, save, env):
        return (1, 1) if elements[0].e_type == e_type.HEADER else (-1, 0)

    def process_modules(self):
        width = self.env["div_width"]
        if width > 25:
            self.size_profile = "normal"
        else:
            self.size_profile = "compact"
            self.add_class("leading-tight")

        if width > 48:
            self.class_list.append("w-1/3")

        level = self.e0.level
        if self.size_profile == "normal":
            size = self.normal[level]
        else:
            size = self.compact[level]
        self.add_class(f"{size} font-semibold text-slate-900")

    def render_str(self):
        level = self.e0.level
        text = self.e0.text
        return render_m_html(self, f"h{level}", text)

    def score(self):
        """
        Metrics:
        - Box Ratio: The textbox for the header should not be too narrow or too wide
        """
        has_width = self.has_attr("w")
        adj_w = (
            tw_w_to_rem(self.get_attr("w"), self.env) if has_width else self.env.get("div_width", 72)
        )
        # a=0.6 biases towards a wider box
        s_0 = score_text_ratio(self, adj_w, a=0.6)

        return s_0

    def __str__(self) -> str:
        txt = trim_text(self.e0.text, 30)
        return f"{self.__class__.__name__}: {txt}"


class M_Paragraph(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].e_type == e_type.PARAGRAPH:
            return 1, 1
        return (-1, 0)

    def process_modules(self):
        width = self.env["div_width"]
        if width > 48:
            self.add_class("text-xl")
            self.font_size = 1.25
            self.font_width = self.e0.font_width * 1.25
        elif width >= 36:
            self.add_class("text-lg")
            self.font_size = 1.125
            self.font_width = self.e0.font_width * 1.125

    def get_width(self, contain=True):
        if contain:
            return self.env.get("div_width")
        return super().get_width(False)

    def get_height(self, contain=True):
        if contain:
            w0 = self.get_width(False)
            w1 = self.get_width(True)
            h = super().get_height()
            rows = math.ceil(w0 / w1)
            return h * rows
        return super().get_height()

    def render_str(self):
        return render_m_html(self, "p", self.e0.get_str())

    def render(self):
        pass

    def __str__(self) -> str:
        texts = self.e0.texts
        txt = "".join(t[1] for t in texts)
        txt = trim_text(txt, 40)
        return f"{self.__class__.__name__}: {txt}"

    def score(self):
        """
        Metrics:
        - Box Ratio: The textbox for the paragraph should not be too narrow or too wide
        - Width: Even if the ratio is good, paragraphs should not be too narrow unless it is very short
        """
        has_width = self.has_attr("w")
        c_width = self.env.get("div_width")
        adj_w = tw_w_to_rem(self.get_attr("w"), self.env) if has_width else c_width
        if adj_w > 70:
            #print(f"{self.__class__.__name__}: {adj_w}")
            return 0
        # print("adj_w", adj_w)
        s_0 = score_text_ratio(self, adj_w)

        txt = self.e0.get_str()
        word_count = len(txt.split())
        if word_count < 8:
            return -1

        s1 = 0 if adj_w > 36 else 1
        # elif c_width < 18:
        #     s_1 = 0.3
        # elif c_width < 24:
        #     s_1 = 0.8
        # else:
        #     s_1 = s_0
        #print(f'{self.__class__.__name__}:\n\t{s_0}\n\t{s1}')

        return (s_0 + s1) / 2


class M_EmText(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].e_type != e_type.PARAGRAPH:
            return -1, 0
        if all(t[0] != "em" for t in elements[0].texts):
            return -1, 0
        return 1, 1

    def render_str(self):
        txt = []
        for t in self.e0.texts:
            if t[0] == "em":
                if "em_size" in self.param:
                    cls = f"text-{self.param['em_size']}"
                else:
                    cls = "text-xl"
                txt.append(f'<strong class="{cls}">{t[1]}</strong>')
            else:
                if "etc_size" in self.param:
                    cls = f"text-{self.param['etc_size']}"
                else:
                    cls = "text-sm"
                txt.append(f'<span class="{cls}">{t[1]}</span>')
        txt = "<br>".join(txt)
        txt = f"<p>{txt}</p>"
        return txt

    def __str__(self) -> str:
        txt = trim_text(self.e0.texts[0], 40)
        return f"{self.__class__.__name__}: {txt}"


class M_Link(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].e_type == e_type.LINK:
            return 1, 1
        return (-1, 0)

    def process_modules(self):
        self.add_class("link")

    def render_str(self):
        url = self.e0.href
        text = self.e0.text
        return f'<a class="{self.class_list_str}" href="{url}">{text}</a>'

    def render(self):
        pass

    def __str__(self) -> str:
        txt = trim_text(self.e0.text, 40)
        return f"{self.__class__.__name__}: {txt}"


class M_TextGeneral(LeafModule):
    def match(elements, param, save, env):
        return 0, 1

    def render_str(self):
        return f"<p>{self.e0.text}</p>\n"

    def render(self):
        pass

    def __str__(self) -> str:
        txt = trim_text(self.e0.text, 40)
        return f"{self.__class__.__name__}: {txt}"


class M_Image(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return -1, 1
        if elements[0].e_tag == "img":
            return 1, 1
        return -1, 1

    def get_aspect_ratio(self):
        return self.e0.aspect_ratio

    def process_modules(self):
        size = self.ctx.get("size", 4)
        size = int(size)

        if size >= 3:
            self.add_class("rounded-xl w-full drop-shadow-xl")
        elif size == 2:
            size_t = int(self.ctx.get("size-t", 3))
            if size_t == 1:
                w = "3/4"
            elif size_t == 2:
                w = "5/6"
            else:
                w = "full"
                self.add_class("rounded-xl")
            self.add_class(f"min-w-0 mx-auto w-{w}")
        elif size == 1:
            size_t = int(self.ctx.get("size-t", 2))
            if size_t == 1:
                size = 8
            elif size_t == 2:
                size = 16
            else:
                size = 32
            self.add_class(f"min-w-0 w-{size}")

        else:
            size = 8
            self.add_class(f"rounded-xl min-w-0 w-{size}")

    def render_str(self):
        return f'<img class="{self.class_list_str}" src="{self.e0.url}"/>'

    def render(self):
        pass

    def score(self):
        size = int(self.ctx.get("size", 4))
        if size < 2:
            return -1
        c_width = self.env.get("div_width", 72)
        # if c_width < 71:
        #     return -1

        if size == 3 and abs(c_width - 36) > 8:
            return 0
        if size == 2 and abs(c_width - 18) > 8:
            return 0

        return -1

    def __str__(self) -> str:
        url = self.e0.url
        url = trim_text(url, 40)
        return f"{self.__class__.__name__}: {url}"


class M_Video(M_Image):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return -1, 1
        if elements[0].e_tag == "video":
            return 1, 1
        return -1, 1

    def process_modules(self):
        size = img_ctx_size(self.e0)

        if size >= 2:
            self.add_class("rounded-xl w-full drop-shadow-xl")
        elif size == 1:
            size_t = int(self.ctx.get("size-t", 2))
            if size_t == 1:
                size = 8
            elif size_t == 2:
                size = 12
            else:
                size = 16
            self.add_class(f"rounded-xl min-w-0 w-{size}")
        else:
            size = 8
            self.add_class(f"rounded-xl min-w-0 w-{size}")

    def render_str(self):
        source = f"<source src='{self.e0.url}' type='video/mp4'>\nUnsupported video."
        return render_m_html(self, "video", source, custom="autoplay='autoplay' muted")

    def score(self):
        size = int(self.ctx.get("size", 4))
        if size < 2:
            return -1
        c_width = self.env.get("div_width", 72)
        if size == 3 and abs(c_width - 36) > 8:
            return 0
        if size == 2 and abs(c_width - 18) > 8:
            return 0

        return -1

    def __str__(self) -> str:
        url = self.e0.url
        url = trim_text(url, 40)
        return f"{self.__class__.__name__}: {url}"


class M_Button(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 1)
        if elements[0].e_tag == "button":
            return (1, 1)
        return (-1, 1)

    def process_modules(self):
        self.add_class("btn")

    def render_str(self):
        href = self.e0.href
        text = self.e0.text
        return render_m_html(self, "button", text, href)

    def render(self):
        pass

    def __str__(self) -> str:
        txt = trim_text(self.e0.text, 40)
        return f"{self.__class__.__name__}: {txt}"


class M_Span(LeafModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 1)
        if elements[0].e_type == e_type.SPAN:
            return 1, 1
        return (-1, 1)

    def render_str(self):
        cls = "badge"
        cls += self.class_list_str
        return f'<span class="{cls}">{self.e0.text}</span>'

    def render(self):
        pass

    def __str__(self) -> str:
        txt = trim_text(self.e0.text, 40)
        return f"{self.__class__.__name__}: {txt}"
