from modules.base import *
from modules.leaf import *
from util import *
import math


class CompactGroup_Col(ColumnModule, BranchModule):
    """
    Elements should be contained in vertical columns if
    they are the same type of elements. In such case, fit as many as possible.
    """

    next_modules = standard_modules

    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        i = 1
        cur = elements[0]
        nxt = elements[i]
        total_height = cur.get_height(env) + nxt.get_height(env)
        max_height = 6

        if cur.e_type == e_type.IMAGE:
            return -1, 0

        while i < len(elements):
            if (
                is_divider(nxt, 2)
                or nxt.e_type == e_type.BUTTON
                or nxt.e_type == e_type.LINK
                or nxt.e_type == e_type.IMAGE
            ):
                break
            if total_height > max_height:
                break
            i += 1
            if i >= len(elements):
                break
            cur = nxt
            nxt = elements[i]
            total_height += nxt.get_height(env)

        if i == 1:
            return -1, 0
        # if cur != nxt:
        #     return -1, 0

        return 1, i

    def process_modules(self):
        if self.env["div_width"] <= 24:
            for m in self.modules:
                if m.elements[0].e_tag == "p":
                    m.param["class_list"].append("text-sm")

    def render_str(self):
        return render_branch_m_html(self, "div")


class CompactGroup_1Row(RowModule, BranchModule):
    """
    Used when group is small enough to fit in one row.
    """

    next_modules = ["CompactGroup_Col"] + m_leaf
    # sub_modules = [
    #     OneRow_HasButton,
    #     OneRow_General
    # ]

    def match(elements, param, save, env):

        parsed = param["parsed_elements"]
        if len(parsed) > 0 and not is_divider(parsed[-1], 0):
            return -1, 0

        i = 0
        while i < len(elements) and not is_divider(elements[i]):
            i += 1
        if i == 0:
            return -1, 0
        total_size = sum(e.get_size(env) for e in elements)

        if total_size > env["div_width"] * 2:
            return -1, 0

        return 1, i

    def element_parse(self, parser):
        self.passthrough_parse(parser)

    def process_modules(self):
        # Buttons should have the same width.
        # Measure the ratio of button width to non-button element width.
        # for m in self.modules:
        #     pprint(m.param, depth=1)
        if len(self.modules) < 2 and self.modules[0].modules is not None:
            self.modules = self.modules[0].modules
            return

        widths = [m.get_width() for m in self.modules]
        total_w = sum(widths)
        ratios = [w / total_w for w in widths]
        ratios_12 = [math.ceil(r * 12) for r in ratios]
        # Ensure the sum of ratios is 12.
        if sum(ratios_12) != 12:
            ratios_12[-1] += 12 - sum(ratios_12)
        # Apply the ratios to the widths.
        for i, m in enumerate(self.modules):
            if is_module_text(m):
                m.add_class(f"basis-{ratios_12[i]}/12")

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        mods = "".join(mods)
        return f'<div class="flex flex-row items-center gap-x-3">{mods}</div>'


class CompactGroup_StackRow(RowModule, BranchModule):

    next_modules = [M_EmText]

    def is_short_stackable_p(e):
        if e.e_tag != "p":
            return False
        p_types = [t[0] for t in e.texts]
        if "em" not in p_types:
            return False
        if any(len(t[1]) >= 20 for t in e.texts):
            return False

        return True

    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        stacks = []
        e = elements[0]
        while CompactGroup_StackRow.is_short_stackable_p(e):
            stacks.append(e)
            if len(stacks) >= len(elements):
                break
            e = elements[len(stacks)]

        if len(stacks) < 1:
            return -1, 0
        return 1, len(stacks)

    def process_modules(self):
        for m in self.modules:
            m.param["stack"] = True

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        return (
            f"<div href='hi' class='{cls} flex-auto flex gap-2'>{''.join(mods)}</div>"
        )


class CompactGroup_Row(RowModule, BranchModule):

    exclude_modules = ["Section_ImgP"]

    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        # param = get_parent_param_by_class(param, "ModuleCard")
        group_width = env["div_width"]
        total_width = 0

        i = 0
        while i < len(elements):
            e = elements[i]
            if is_divider(e):
                break
            i += 1
        next_break = i

        i = 1
        cur = elements[0]
        nxt = elements[i]

        total_width += cur.get_width(env)

        while True:
            if cur.e_type != nxt.e_type:
                break
            if cur.e_type == e_type.HEADER and cur.e_tag != nxt.e_tag:
                break
            if is_divider(nxt):
                break
            if i >= len(elements) - 1:
                break

            total_width += nxt.get_width(env)
            i += 1
            cur = nxt
            nxt = elements[i]

        if i == 1:
            return -1, 0
        if total_width > group_width:
            return -1, 0
        if cur.e_type == nxt.e_type and i != next_break:
            return -1, 0

        return 1, i

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        if len(mods) == 1:
            return mods[0]
        return f"<div class='flex-auto flex gap-2 flex-wrap'>{''.join(mods)}</div>"


class CompactGroup_SpanRow(RowModule, BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        i = 0
        while i < len(elements):
            e = elements[i]
            if e.e_tag != "span":
                break
            i += 1

        if i < 2:
            return -1, 0

        return 1, i

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        return f"<div class='flex-auto flex gap-2 flex-wrap'>{''.join(mods)}</div>"


class CompactGroup_ButtonRow(RowModule, BranchModule):
    def match(elements, param, save, env):

        if len(elements) < 2:
            return -1, 0

        i = 0
        while i < len(elements):
            e = elements[i]
            if e.e_tag != "button":
                break
            i += 1

        if i < 2:
            return -1, 0

        return 1, i

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        return f"<div class='flex-auto flex gap-2 flex-wrap'>{''.join(mods)}</div>"


class CompactGroup_MixedRow(CompactGroup_1Row):
    def match(elements, param, save, env):
        # Find end of elements or next hr
        i = 0
        while i < len(elements):
            e = elements[i]
            if is_divider(e):
                break
            i += 1
        s = {}
        score, count = CompactGroup_1Row.match(elements[:i], param, s, env)
        # print(score, count)
        # print(i, len(elements))
        if count != len(elements) and count != i:
            return -1, 0
        parsed_ele = param["parsed_elements"]
        if len(parsed_ele) > 0 and parsed_ele[-1].e_tag != "hr":
            return -1, 0

        save.update(s)
        return score, count

    def process_modules(self):
        if len(self.modules) == 1 and is_module_group(self.modules[0]):
            self.modules[0].add_classes(self.class_list)
            self.modules = self.modules[0].modules

    def render_str(self):

        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        return f"<div class='{cls} flex-auto flex gap-2'>{''.join(mods)}</div>"


class CompactGroup_NRow(ColumnModule, BranchModule):
    """
    Used when group needs multiple rows to fit.
    """

    next_modules = [
        "CompactGroup_StackRow",
        "CompactGroup_Row",
        "CompactGroup_SpanRow",
        "CompactGroup_MixedRow",
    ] + m_leaf

    def match(elements, param, save, env):
        return 0, len(elements)

    def element_parse(self, parser):
        self.passthrough_parse(parser)

    def process_modules(self):
        # cur_type = self.modules[0].param["specific_type"]
        # for m in self.modules[1:]:
        #     typ = m.elements[0].e_type
        #     if cur_type != typ:
        #         m.param["class"] = "mt-8"
        #     cur_type = typ

        next_mt = False
        for m in self.modules:
            if next_mt:
                m.add_class("mt-4")
                next_mt = False
            if m.elements[0].e_tag == "hr":
                next_mt = True

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        return f"{''.join(mods)}"


# class CompactRow(BranchModule):


class CompactGroup(ColumnModule, BranchModule):
    """
    This module handles a group that is constrained in a small space,
    such as the paragraph of a TextImage Module or elements in a card layout.

    Width is often limited, so compared to other Group modules, this module
    has a tendency to make as many elements as inline as possible, especially
    for images.
    """

    next_modules = [
        CompactGroup_1Row,
        CompactGroup_NRow,
    ]

    def match(elements, param, save, env):
        return 1, len(elements)

    def element_parse(self, parser):
        self.passthrough_parse(parser)


class Card_Body(ColumnModule, BranchModule):
    def match(elements, param, save, env):
        return 1, len(elements)

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        return f"<div class='card-body {cls}'>{''.join(mods)}</div>"


class Card_Image(ColumnModule, BranchModule):
    def match(elements, param, save, env):
        return 1, len(elements)

    def process_modules(self):
        # Find the image
        self.modules = self.modules[0].modules[0].modules
        img = self.modules[0]
        img.add_class("object-cover h-full")
        img.remove_attr("rounded")
        # Based on the width of the container and eq_avg_aspect_ratio (if applicable),
        # determine the height of the image
        mc = get_parent_param_by_class(self.param, "ModuleCard")
        container_width = mc["self"].env["div_width"]
        ratio = img.get_aspect_ratio()
        # print(f"Container width: {container_width}")
        height = math.floor(container_width * ratio)
        height = height // 4 * 4
        self.add_class(f"h-{height * 4} overflow-hidden")
        self.param["height"] = height
        self.param["fig_height"] = height

    def render_str(self):
        # print("Card_Image")
        # pprint(self.param, depth=1)
        img = self.modules[0]
        render = img.render_str()
        cls = self.class_list_str
        return f"<figure class='{cls}'>{render}</figure>"


class Card_FloatingBody(BranchSubModule):
    def match(module, param):
        modules = module.modules
        if len(modules) < 2:
            # print(f"Not enough modules")
            return -1
        if not isinstance(modules[0], Card_Body):
            # print(f"First module is not a Card_Image")
            return -1
        if not isinstance(modules[1], Card_Image):
            # print(f"Second module is not a Card_Body")
            return -1
        card_body = modules[0]
        card_img = modules[1]

        # print(card_body.modules[0].modules[0].modules)
        if any(not is_module_text(m) for m in card_body.modules[0].modules[0].modules):
            # print(f"Card_Body does not contain text")
            return -1

        return 1

    def process_modules(self):
        card_body = self.modules[0]
        card_body.add_class("absolute top-0 pt-6")
        body_total_height = sum(
            m.get_height() for m in card_body.modules[0].modules[0].modules
        )
        bth = body_total_height // 8 * 4
        card_img = self.modules[1]
        img_height = card_img.param["height"]
        card_img.add_class(f"h-{bth+img_height}")

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        cls += " card bg-base-100 shadow-xl align-self-start"
        return f"<div class='{cls}'>{''.join(mods)}</div>"


class Card_OverlapImage(BranchSubModule):
    def match(module, param):
        # print(f"Matching Card_OverlapImage")
        modules = module.modules
        if len(modules) < 2:
            # print(f"Not enough modules")
            return -1
        if not isinstance(modules[0], Card_Image):
            # print(f"First module is not a Card_Image")
            return -1
        if not isinstance(modules[1], Card_Body):
            # print(f"Second module is not a Card_Body")
            return -1
        card_img = modules[0]
        card_body = modules[1]
        # print(f"Card_Body: {card_body}")

        first_mod = flatten_modules(card_body, 2)[0]
        # print(f"First module is {first_mod.modules[0].__class__.__name__}")
        if isinstance(first_mod, CompactGroup_1Row):
            # print(f"Card_Body has a CompactGroup_1Row")
            return -1

        first_mod = flatten_modules(first_mod)[0]

        if first_mod.m_main_type != e_type.IMAGE:
            # print(f"First module {first_mod.__class__}, {first_mod.m_main_type} is not an image")
            return -1
        if int(first_mod.e0.ctx["size"]) != 1:
            # print(first_mod.element.ctx)
            # print(f"First module is not an icon image")
            return -1

        param["img"] = first_mod
        return 1

    def process_modules(self):
        figure = self.modules[0]
        fig_img = figure.modules[0]
        card_body = self.modules[1]
        img = self.param["img"]

        figure.remove_class("overflow-hidden")
        fig_height = figure.param["fig_height"]
        # print(f"fig_height: {fig_height}")
        # img_width = img.get_width()
        img_height = img.get_height()
        # print(f"Image height: {img_height}")
        fig_img.add_class(f"h-[{(fig_height + img_height / 2)}rem]")
        fig_img.add_class("absolute top-0")
        fig_img.remove_class("h-full")

        img.add_class("border-2 border-white")

        card_body.add_class("pt-0 z-10")

    def render_str(self):
        # pprint(self.param, depth=1)
        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        cls += " card bg-base-100 shadow-xl align-self-start"
        return f"<div class='{cls}'>{''.join(mods)}</div>"


class ModuleCard(ColumnModule, BranchModule):
    """
    A card is a group of elements that are constrained in a small space.
    """

    next_modules = [
        CompactGroup,
    ]

    sub_modules = [
        Card_OverlapImage,
        Card_FloatingBody,
    ]

    custom_param = {"e_main_type": "compact_group"}

    def match(elements, param, save, env):
        if len(elements) < 1:
            return 0, 0
        if "card" in elements[0].e_class:
            return 2, 1
        return -1, 0

    def render_str(self):
        # print memory address of self.param
        # pprint(self.param, depth=1)
        if self.sub_module is not None:
            return self.sub_module.render_str()
        mods = [m.render_str() for m in self.modules]
        cls = self.class_list_str
        cls += " card bg-base-100 shadow-xl align-self-start"
        return f"<div class='{cls}'>{''.join(mods)}</div>"

    def process_elements(self):
        g_elements = [[]]
        for e in self.elements[0].elements:
            if e.e_tag == "img" and int(e.ctx.get("size", 0)) >= 4:
                g_elements.append([e])
                g_elements.append([])
            else:
                g_elements[-1].append(e)

        self.g_elements = g_elements
        self.param["g_elements"] = g_elements

        # grp_param = get_parent_param_by_class(self.param, "ModuleCardGroup")
        # grp_cols = grp_param["cols"]
        # grp_width = grp_param["group_width"]
        # self.param["group_width"] = grp_width / grp_cols

    def element_parse(self, parser):
        for ele in self.g_elements:
            if len(ele) == 0:
                continue
            mods = parser(ele, self.param, self.next_modules, self.child_env)
            if ele[0].e_tag == "img" and int(ele[0].ctx.get("size", 0)) >= 4:
                container = Card_Image(ele, self.param, self.child_env)
            else:
                container = Card_Body(ele, self.param, self.child_env)
            container.modules = mods
            container.process_modules()
            self.modules.append(container)


class ModuleCardGroup(VarModule, BranchModule):
    next_modules = [
        ModuleCard,
    ]

    passthrough = True

    def match(elements, param, save, env):
        if len(elements) < 1:
            return 0, 0
        i = 0
        while i < len(elements) and "card" in elements[i].e_class:
            i += 1
        if i < 1:
            return -1, 0
        return 1.5, i

    def process_elements(self):

        # self.child_env["div_width"] = self.env["div_width"] / 3

        # sizes = [e.get_size(self.env) for e in self.elements]
        # avg_size = sum(sizes) / len(sizes)
        # max_size = max(sizes)
        # count = len(self.elements)
        c_width = self.env["div_width"]

        cols = [1, 2, 3, 4]
        scores = []
        for col in cols:
            tmp_env = self.child_env.copy()
            tmp_env["div_width"] = c_width / col
            tmp_p = self.param.copy()
            tmp_p["cols"] = col
            #print(f"Trying {col} columns")
            score = self.parse_search_tree(
                self.elements, tmp_p, self.env, tmp_env, True
            )
            scores.append((score, col))
        #print("Scores", scores)
        best_cw = max(scores, key=lambda x: x[0])
        best_cols = best_cw[1]

        self.param["cols"] = best_cols

        # grp_param = get_parent_param_by_type(self.param, e_type.GROUP)
        # self.param["group_width"] = self.env["div_width"] / cols

    def process_modules(self):
        if "eq_group" not in self.param or self.param["eq_group"] == False:
            for m in self.modules:
                m.add_class("self-start")

    def render_str(self):
        mods = [m.render_str() for m in self.modules]
        cols = self.param["cols"]
        return f"<div class='gap-8 grid grid-cols-{cols}'>{''.join(mods)}</div>"
