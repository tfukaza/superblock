from modules.base import *
from modules.leaf import *
from modules.compact import *
from util import *
from process import *


class M_Section(ColumnModule, BranchModule):

    # passthrough = True
    next_modules = ["Section_Repeat"] + m_section + standard_modules

    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 1)
        if elements[0].e_tag == "section":
            return 1.5, 1
        return (-1, 1)

    def process_modules(self):
        m_add_margins(self.modules)

    def render_str(self):
        # print(f"{self.__class__.__name__}")
        # print(f"Render: {self.modules}")
        module_render = [m.render_str() for m in self.modules]
        return (
            "<section class='py-20'><div class='mx-auto w-[1080px]'>"
            + "".join(module_render)
            + "</div></section>"
        )

# class M_Landing(ColumnModule, BranchModule):
#     """
#     A Section Module specifically for landing pages. 
#     It has special scoreing functions just for landings.  
#     """

#     next_modules = m_section + standard_modules

#     def match(elements, param, save, env):
        
#         if elements[0].e_tag == "section" and elements[0].e_class == "landing":
#             return 2, 1
#         return (-1, 1)

#     def process_modules(self):
#         m_add_margins(self.modules)

#     def render_str(self):
#         module_render = [m.render_str() for m in self.modules]
#         return (
#             "<section class='mx-auto py-20 w-[1080px]'>"
#             + "".join(module_render)
#             + "</section>"
#         )
    
#     def score(self):
#         """
#         https://www.youtube.com/watch?v=flAcHu-squc
#         Metrics:
#         - Awareness: User knows what website they are looking at  
#         - Hierarchy: Clear flow of content
#         - Call to action: No more than 1 CTA
#         """
#         pass

# class Section_RelatedElements(BranchModule):
#     """
#     This module matches all elements until the next hr,
#     assuming that they are contextually related.
#     The elements are then divided into groups using vr as seperators. 
#     """
#     def match(elements, param, save, env):

#         if len(elements) < 1:
#             return -1, 0
        
#         sub_ele = e_until_next_hr(elements)
#         if len(sub_ele) < 2:
#             return -1, 0
        
#         return 1, len(sub_ele)
        # if is_element_group(sub_ele[0]):
        #     sub_ele = sub_ele.elements
class Section_FullImg(RowModule, BranchModule):

    exclude_modules = ["Section_FullImg"]
    passthrough = True

    def match(elements, param, save, env):

        if len(elements) < 2:
            return -1, 0

        sub_ele = elements
        if is_element_text(sub_ele[0], allow_group=True) and is_element_img(sub_ele[1], 4):
            save["text"] = sub_ele[0]
            save["img"] = sub_ele[1]
            save["img_first"] = False
            return 1, 2
        if is_element_img(sub_ele[0], 4) and is_element_text(sub_ele[1], allow_group=True):
            save["text"] = sub_ele[1]
            save["img"] = sub_ele[0]
            save["img_first"] = True
            return 1, 2
        
        return -1, 0

    def process_elements(self):
        c_width = self.env["div_width"]
        img = self.param["img"]
        self.param["img_ratio"] = img.aspect_ratio
        area, x_start, y_start, width, height = img_max_rect(img.url, (255,255,255))

        txt_width = int(c_width * width)
        self.child_env["div_width"] = txt_width
        self.param["area"] = area
        self.param["x_start"] = x_start
        self.param["y_start"] = y_start
        self.param["i_width"] = width
        self.param["i_height"] = height

    def process_modules(self):
        if self.param["img_first"]:
            img = self.param["m_img"] = self.modules[0]
            txt = self.param["m_txt"] = self.modules[1]
        else:
            txt = self.param["m_txt"] = self.modules[0]
            img = self.param["m_img"] = self.modules[1]
        
        area = self.param["area"]
        x_start = self.param["x_start"]
        y_start = self.param["y_start"]
        width = self.param["i_width"]
        height = self.param["i_height"]
        c_width = self.env["div_width"]
        ratio = self.param["img_ratio"]
        
        txt_w = "w-" + tw_float_to_w(width, True) or "full"
        x = int(x_start*c_width*16)//4
        x = f"ml-{x}"
        y = int(y_start*c_width*ratio*16)//4
        y = max(8, y)
        y = f"mt-{y}"
        txt.add_class(f"{txt_w} {x} {y}")

        self.remove_attr("grid-cols")
        self.add_class("h-1/2 overflow-hidden relative")
        img.add_class("w-full absolute -z-50")        

    def render_str(self):
        img = self.param["m_img"]
        img = img.render_str()
        txt = self.param["m_txt"]
        txt = txt.render_str()
        href = self.param["img"].url
        cls = self.class_list_str
        return f"<div class='{cls}'>{img}{txt}</div>"
        # style='background-image: url({href});'

class Section_ImgP(RowModule, BranchModule):

    # sub_modules = [Multiple_Paragraphs
    exclude_modules = ["Section_ImgP"]
    #sub_modules = ["S_FullImgLanding"]

    passthrough = True

    def match(elements, param, save, env):

        if len(elements) < 2:
            return -1, 0
        
        c_width = env["div_width"]
        # if c_width < 70:
        #     return -1, -0
        # sub_ele, _ = e_until_next_hr(elements)
        # if len(sub_ele) < 2:
        #     return -1, 0
        sub_ele = elements
        # print(sub_ele)
        # print(is_element_img(sub_ele[0], 3), is_element_text(sub_ele[1], allow_group=True))
        
        if (is_element_text(sub_ele[0], allow_group=True) and is_element_img(sub_ele[1], 3) or 
            is_element_img(sub_ele[0], 3) and is_element_text(sub_ele[1], allow_group=True)):
            return 1, 2
        
        #print("No")
        return -1, 0
      

    def process_elements(self):
        c_width = self.env["div_width"]
        trials = []
        for col in [1, 2]:
            trials.append((
                {"cols": col},
                {},
                {"div_width": c_width/col},
            ))
        _, best, scores = self.search_matches(trials, True)
        best_param = best[0]
        best_cols = best_param["cols"]

        self.param["cols"] = best_cols
        self.child_env["div_width"] = self.env["div_width"] / best_cols
        # self.child_env["direction"] = "column"
        # self.x_starts = [0, self.child_env["div_width"]]

    def process_modules(self):
        if is_element_img(self.elements[0]):
            self.param["img"] = self.elements[0]
            self.param["txt"] = self.modules[1]
        else:
            self.param["img"] = self.elements[1]
            self.param["txt"] = self.modules[0]
        m_add_margins(self.modules[0].modules, 6, 8)
        m_add_margins(self.modules[1].modules, 6, 8)

        if len(self.param["txt"].modules) < self.param["cols"]:
            self.param["cols"] = len(self.modules)
        if self.param["cols"] == 1:
            pass
        else:
            self.add_class("grid grid-cols-2 gap-16 items-center")

    def render_str(self):

        # m_1 = "".join(m.render_str() for m in self.new_modules[0])
        # m_2 = "".join(m.render_str() for m in self.new_modules[1])
        # m_1 = f"<div>{m_1}</div>"
        # m_2 = f"<div>{m_2}</div>"
        # class_name = self.__class__.__name__
        if self.sub_module is not None:
            return self.sub_module.render_str()
        return render_branch_m_html(self, "div")

class Section_Repeat(VarModule, BranchModule):
    """
    Detects a repeating pattern of elements
    """

    #exclude_modules = ["Section_ImgP"]


    def match(elements, param, save, env):
        if len(elements) < 2:
            return -1, 0

        if elements[0].e_type == e_type.DIVIDER:
            return -1, 0

        same_hashes = [(0, 0)]
        for i in range(1, len(elements)):
            ele = [elements[j : j + i] for j in range(0, len(elements), i)]
            hashes = [[e.get_struct_hash(depth=1) for e in el] for el in ele]
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
        return 1.5, max_hash[0] * max_hash[1]

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


    def element_parse(self, parser):
        g_elements = self.param["elements"]
        cols = self.param["cols"] 
        d_w = self.child_env["div_width"]

        i = 0
        #print("hi")
        for ele in g_elements:
            #print(ele)
            #ele = [e for e in ele if e.e_type != e_type.DIVIDER]
            if not ele:
                continue
            self.child_env["x_current"] = (i%cols)*d_w
            mods = parser(ele, self.param, self.next_modules, self.child_env)
            gg = strings_to_classes(["M_GroupGeneral"])[0]
            container = gg(ele, self.param, self.child_env)
            container.modules = mods
            container.process_modules()
            self.modules.append(container)
            i += 1
        # print("rep1", self.param["module_index"], self.modules)
        self.param["modules"] = self.modules

    def render_str(self):
        return render_branch_m_html(self, "div", env=self.env)