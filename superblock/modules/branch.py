import statistics
from modules.base import *
from modules.leaf import *
from modules.compact import *
from module_list import *
from process import *
from util import *


class M_GroupGeneral(ColumnModule, BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        count = 0
        for e in elements:
            if is_element_group(e):
                count += 1
            else:
                break
        if count > 0:
            return (0, count)
        return (-1, 0)

    def process_modules(self):
        c_width = self.env["div_width"]
        if c_width > 48:
            p = [8, 12]
        elif c_width > 24:
            p = [4, 8]
        else:
            p = [1, 2]
        m_add_margins(self.modules, *p)

    def render_str(self):
        return render_branch_m_html(self, "div", optimize=True, env=self.env)


class M_GroupList(BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].e_type == e_type.LIST:
            return (1, 1)
        return (-1, 0)

    def render_str(self):
        r = [f"<li>{m.render()}</li>" for m in self.modules]
        return f"<ol class='{self.class_list_str}'>" + "".join(r) + "</ol>"


class M_ButtonRow(RowModule, BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return -1, 0
        i = 0
        for e in elements:
            if e.e_type == e_type.BUTTON:
                i += 1
            else:
                break
        if i > 0:
            return 1, i
        return -1, 0

    def process_modules(self):
        self.add_class("flex gap-2")

    def render_str(self):
        return render_branch_m_html(self, "div", optimize=True)


class M_IconRow(RowModule, BranchModule):

    exclude_modules = ["Section_ImgP"]

    def match(elements, param, save, env):
        if len(elements) < 1:
            return -1, 0
        i = 0
        for e in elements:
            if e.e_type == e_type.IMAGE and img_ctx_size(e) < 2:
                i += 1
            else:
                break
        if i > 0:
            return 1, i
        return -1, 0

    def process_modules(self):
        self.add_class("flex gap-2")

    def render_str(self):
        s = [m.render_str() for m in self.modules]
        s = "".join(s)
        return f"<div class='{self.class_list_str}'>{s}</div>"


class M_MultiP(VarModule, BranchModule):

    next_modules = [
        "M_Paragraph",
    ]
    passthrough = True

    def match(elements, param, save, env):
        i = 0
        # if env["div_width"] < 18:
        #     return -1, 0

        for e in elements:
            if not e.e_tag == "p":
                break
            i += 1

        if i > 0:
            return 1.5, i
        return -1, 0

    def process_elements(self):
        # Try out different column widths and see which one is best.
        c_width = self.env["div_width"]
        # print(c_width)
        # Given how many paragraphs there are and the width of the div,
        # run a search tree to determine the best number of columns.
        # TODO allow multiple rows if needed
        cols = [i for i in range(1, min(5, len(self.elements) + 1))]
        d = standard_widths
        if c_width > 70:
            widths = [k for k in d.keys()]
            # cols = [2, 3, 4]
        else:
            widths = ["full"]

        trials = []
        for col in cols:
            for width in widths:
                trials.append((
                    {"cols": col, "b_width": width},
                    {},
                    {"div_width": c_width*d[width]/col},
                ))
        _, best, _ = self.search_matches(trials, True)
        best_param = best[0]
        best_width = best_param["b_width"]
        best_cols = best_param["cols"]

        self.param["b_width"] = best_width
        self.param["cols"] = best_cols
        self.env["div_width"] = c_width * d[best_width]
        self.child_env["div_width"] = self.env["div_width"] / best_cols

    # def get_height(self):
    #     m_count = len(self.modules)
    #     cols = self.param["cols"]
    #     rows = math.ceil(m_count / cols)
    #     m_rows = [list(self.modules[i*cols:(i+1)*cols]) for i in range(rows)]
    #     return sum(max(m.get_height() for m in mods) for mods in m_rows)

    def score(self):
        d = standard_widths
        # Looks at the width of this container, the number of columns,
        # and the number of paragraphs in this container.
        # It evaluates the distance between the end of each paragraph
        # and the start of the next paragraph.
        s0 = super().score()
        s1 = score_p_eyetrack(self.modules, self.env)
        # Prefers to have less whitespace
        diff = self.param["cols"] - len(self.modules)
        s2 = sigmoid(-diff, 3) if diff != 0 else 1
        width = self.param["b_width"]
        s3 = 1 if width == "full" else d[width]
        if self.param["cols"] == 1 and width == "full" and self.env["div_width"] > 60:
            return 0.0
        #print(f"{s0} {s1} {s2} {s3}")
        return filter_scores([s0, s0, s0, s0, s1, s2, s3])

    def process_modules(self):
        cols = self.param["cols"]
        best_width = self.param["b_width"]
        # self.remove_attr("w")

        self.add_class(f"w-{best_width}")
        if cols != 1 or len(self.modules) != 1:
            self.add_class(f"gap-8 grid grid-cols-{cols}")

    def render_str(self):
        return render_branch_m_html(self, "div", optimize=False, env=self.env)


class M_TextGroup(ColumnModule, BranchModule):

    # Group of text elements
    next_modules = [
        "M_MultiP",
        "M_GroupGeneral",
    ] + m_leaf

    passthrough = True

    def match(elements, param, save, env):
        i = 0
        for e in elements:
            if not is_element_text(e) and not e.e_tag == "button":
                break
            i += 1

        if i > 1:
            return 1, i
        return -1, 0

    def process_modules(self):
        c_width = self.env["div_width"]
        if c_width > 48:
            p = [8, 8]
        elif c_width > 24:
            p = [4, 6]
        else:
            p = [1, 2]   
        
        m_add_margins(self.modules, *p)
        m_group_horizontal_compact(self)

    # def score(self):
    #     score = super().score()
    #     narrow = 0.7 if self.env["div_width"] <= 12 else 1
    #     return (score + narrow) / 2

    def render_str(self):
        return render_branch_m_html(self, "div", optimize=False)




class M_1Row(RowModule, BranchModule):
    """
    Used when group is small enough to fit in one row.
    """

    next_modules = ["CompactGroup_Col"] + standard_modules
    exclude_modules = ["M_1Row"]

    passthrough = True

    def match(elements, param, save, env):
        parsed = param["parsed_elements"]
        if len(parsed) > 0 and not is_divider(parsed[-1], 0):
            return -1, 0

        i = 0
        while (
            i < len(elements)
            and not is_divider(elements[i], 1)
            and not (is_element_img(elements[i]) and get_img_size(elements[i]) > 1)
        ):
            i += 1

        if i < 2:
            return -1, 0
        total_size = sum(e.get_size(env) for e in elements)

        if total_size > env["div_width"] * 5:
            return -1, 0

        # Find the index of first text element
        j = 0
        while j < i and not is_element_text(elements[j]):
            j += 1

        if any(not is_element_text(e) for e in elements[j:i]):
            return -1, 0

        return 1, i

    def process_elements(self):
        self.child_env["div_width"] = self.env["div_width"] * 0.9

    def process_modules(self):
        self.add_class("flex flex-row items-start gap-x-3")

    def render_str(self):
        return render_branch_m_html(self, "div", optimize=False)


# class RepeatCol_Base(BranchModule):
#     def match(elements, param, save, env):
#         pass


# class RepeatCol_1(RepeatCol_Base):
#     def match(elements, param, save, env):
#         c_width = env["div_width"] / 1
#         g_elements = env["elements"]


class M_RepeatGroup(VarModule, BranchModule):
    """
    Detects a repeating pattern of elements
    """

    exclude_modules = ["Section_ImgP"]


    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        if elements[0].e_type == e_type.DIVIDER:
            return -1, 0

        same_hashes = [(0, 0)]
        for i in range(1, len(elements)):
            ele = [elements[j : j + i] for j in range(0, len(elements), i)]
            hashes = [[e.get_struct_hash() for e in el] for el in ele]
            hashes = ["".join(h) for h in hashes]

            first_hash = hashes[0]
            same_hash = 1
            for h in hashes[1:]:
                if h != first_hash:
                    break
                same_hash += 1
            same_hashes.append((i, same_hash))
        # print(same_hashes)
        max_hash = max(same_hashes, key=lambda x: x[1])
        if max_hash[1] < 2:
            return -1, 0

        save["e_per_grp"] = max_hash[0]
        if max_hash[0] < 1 or (max_hash[0] == 1 and elements[0].e_type != e_type.GROUP):
            return -1, 0
        return 1.6, max_hash[0] * max_hash[1]

    def process_elements(self):
        n = self.param["e_per_grp"]
        g_elements = [self.elements[i : i + n] for i in range(0, len(self.elements), n)]
        #self.child_env["e_per_grp"] = n
        #self.child_env["elements"] = g_elements
        self.param["elements"] = g_elements

        # Determine how many columns we should give to each group
        c_width = self.env["div_width"]
        cols = [1, 2, 3, 4]
        widths = ["full"]
        # Check if the previous module has a width less then 'full'
        # If so, test widths that are less than full, as we can possibly
        # fit all elements in one row. 
        # TODO? : ensure size of prev <= size of this module
        # TODO?: create a Section module that tests out various cols
        # prev = self.param["prev"]
        # if prev and prev.has_attr("w") and tw_w_to_float(prev.get_attr("w")[2:]) < 0.6:
        widths.extend(["2/3", "3/4"])

        trials = []
        for col in cols:
            for width in widths:
                trials.append((
                    {"cols": col, "b_width": width, "col_width": None},
                    {},
                    {"div_width": c_width*tw_w_to_float(width)/col},
                ))
        _, best, scores = self.search_matches(trials, True)
        best_param = best[0]
        best_width = best_param["b_width"]
        best_cols = best_param["cols"]

        if best_width != "full":
            col_width = best_width
            best_width= "full"
        else:
            col_width = None

        # If best width was not 'full', it mean we can put this 
        # repeat group and the previous module in one row AND
        # the UX actually improves.
        # Record it, and allow it to be processed by submodules later
        # if best_width != "full":
        #     self.param["alt_b_width"] = best_width
        #     self.param["alt_cols"] = best_cols
        #     self.param["row_id"] = self.m_id
        #     prev.param["row_id"] = self.m_id
        #     non_full = filter(lambda x: x[1][0]["b_width"] == "full", scores)
        #     best_non_full = max(non_full, key=lambda x: x[0])
        #     best_width = best_non_full[1][0]["b_width"]
        #     best_cols = best_non_full[1][0]["cols"]


        self.param["cols"] = best_cols
        self.param["b_width"] = best_width
        self.param["col_width"] = col_width
        self.child_env["div_width"] = self.env["div_width"] / best_cols

    def process_modules(self):
        best_cols = self.param["cols"]
        best_width = self.param["b_width"]
        col_width = self.param["col_width"]
        self.add_class(f"grid grid-cols-{best_cols} gap-8")
        self.add_class(f"w-{best_width}")   
        # if best_cols == 1:
        #     self.add_class("auto-rows-fr")

        if col_width is not None:
            #self.add_class("text-center")
            for m in self.modules:
                m.add_class(f"w-{col_width} mx-auto")

    def score(self):
        s0 = super().score()
        cols = self.param["cols"]
        width = self.param["b_width"]
        ele = self.param["elements"]

        s1 = 0.0 if len(ele) % cols != 0 else 1
        p_mods = flatten_modules_list(self.modules, 2)
        p_mods = [m for m in p_mods if m.e0.e_tag == "p"]
        if len(p_mods) < 2:
            s2 = -1
        else:
            s2 = score_p_eyetrack(p_mods, self.env)
        
        # For every row, calculate the variance in height
        vrs = []
        if cols != 1:
            for i in range(0, len(self.modules), cols):
                row = self.modules[i : i + cols]
                row_heights = [m.get_height() for m in row]
                if len(row_heights) < 2:
                    vrs.append(0)
                    continue
                row_var = statistics.variance(row_heights)
                var = math.sqrt(row_var) * 2
                vrs.append(var)
            s3 = 1 - (sum(vrs) / len(vrs))
        else:
            s3 = -1
        s4 = -1 #tw_w_to_float(width) 

        scores = [s0, s1, s2, s3, s4]
        return filter_scores(scores)

    def element_parse(self, parser):
        g_elements = self.param["elements"]
        cols = self.param["cols"] 
        d_w = self.child_env["div_width"]

        i = 0
        for ele in g_elements:
            ele = [e for e in ele if e.e_type != e_type.DIVIDER]
            if not ele:
                continue
            self.child_env["x_current"] = (i%cols)*d_w
            mods = parser(ele, self.param, self.next_modules, self.child_env)
            container = M_GroupGeneral(ele, self.param, self.child_env)
            container.modules = mods
            container.process_modules()
            self.modules.append(container)
            i += 1
        # print("rep1", self.param["module_index"], self.modules)
        self.param["modules"] = self.modules

    def render_str(self):
        return render_branch_m_html(self, "div", env=self.env)

    # def get_height(self, contain=True):
    #     m_count = len(self.modules)
    #     cols = self.param["cols"]
    #     rows = math.ceil(m_count / cols)
    #     m_rows = [list(self.modules[i*cols:(i+1)*cols]) for i in range(rows)]
    #     return sum(max(m.get_height() for m in mods) for mods in m_rows)

class M_Body(ColumnModule, BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 1)
        if is_element_group(elements[0]) and elements[0].e_tag == "body":
            return 2, 1
        return (-1, 1)

    def render_str(self):
        module_render = [m.render_str() for m in self.modules]
        return "<body>" + "".join(module_render) + "</body>"
