from modules.base import *
from modules.leaf import *

from module_list import *


class ModuleFooterLogo(BranchModule):
    def match(elements, param, save, env):
        # print("matching", elements)
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].info["e_main_type"] == "group" and "logo" in elements[0].e_class:
            return (1, 1)
        else:
            return (-1, 0)

    def specific_analyze(self):
        return {"footer_module": "logo"}

    def __str__(self) -> str:
        return "<div class='logo'>" + self.modules[0].__str__() + "</div>"


class ModuleFooterCopyright(BranchModule):
    def match(elements, param, save, env):
        # print("matching", elements)
        if len(elements) < 1:
            return (-1, 0)
        if (
            elements[0].info["e_main_type"] == "group"
            and "copyright" in elements[0].e_class
        ):
            return (1, 1)
        else:
            return (-1, 0)

    def specific_analyze(self):
        return {"footer_module": "copyright"}

    def __str__(self) -> str:
        return self.modules[0].__str__()


class ModuleFooterSocialMediaList(BranchModule):
    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        e0 = elements[0]
        # print("matching", e0)
        a = e0.info["e_main_type"] == "group"
        b = e0.e_type == "list"

        if a and b:
            return (1, 1)

        c = a and all(e.e_type == "link" for e in e0.elements)
        if c:
            return (1, 1)
        return (-1, 1)

    def __str__(self):
        # self.modules[0].param["class"] = "social-media"
        r = [f"<li>{str(m)}</li>" for m in self.modules]
        return "<ol class='social-media'>" + "".join(r) + "</ol>"


class ModuleFooterSocialMedia(BranchModule):

    next_modules = [ModuleFooterSocialMediaList]

    def match(elements, param, save, env):
        # print("matching", elements)
        if len(elements) < 1:
            return (-1, 0)
        if (
            elements[0].info["e_main_type"] == "group"
            and "social-media" in elements[0].e_class
        ):
            return (1, 1)
        else:
            return (-1, 0)

    def specific_analyze(self):
        return {"footer_module": "social-media"}

    def __str__(self) -> str:
        return self.modules[0].__str__()


class ModuleFooterMisc(BranchModule):
    def match(elements, param, save, env):
        # print("matching", elements)
        if len(elements) < 1:
            return (-1, 0)
        if elements[0].info["e_main_type"] == "group" and "misc" in elements[0].e_class:
            return (1, 1)
        else:
            return (-1, 0)

    def specific_analyze(self):
        return {"footer_module": "misc"}


class Footer_Links(ColumnModule, BranchModule):

    next_modules = m_leaf

    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 0)
        e0 = elements[0]
        # print("matching", e0)
        if "links" in e0.e_class or e0.e_tag in ["ol", "ul"]:
            return (1, 1)
        return (-1, 1)

    def process_modules(self):
        for m in self.modules:
            m.add_class("text-sm no-underline text-gray-500")
        pass
    
    def render_str(self):
        content = "".join(f"<li class='my-1'>{m.render_str()}</li>" for m in self.modules)
        return render_m_html(self, "ol", content)

    # def __str__(self):
    #     cols = self.grand_parent_param.get("cols", 1)
    #     if cols == 1:
    #         renders = [f"<li>{m}</li>" for m in self.modules]
    #         return f"<ol class='links'>{''.join(renders)}</ol>"
    #     else:
    #         l_per_col = self.grand_parent_param.get("max_height", 100)
    #         renders = []
    #         for i in range(0, len(self.modules), l_per_col):
    #             mod = self.modules[i : i + l_per_col]
    #             r = [f"<li>{m}</li>" for m in mod]
    #             r = "".join(r)
    #             renders.append(r)
    #         renders = (
    #             f"<ol class='links'>"
    #             + "</ol><ol class='links'>".join(renders)
    #             + "</ol>"
    #         )
    #     return renders

    # def __str__(self):
    #     r = [f"<li>{m}</li>" for m in self.modules]
    #     return f"<ol class='links'>{''.join(r)}</ol>"


class Footer_LinkList(ColumnModule, BranchModule):
    """
    ModuleFooterLinkList is the container for Modules representing the footer link list.
    It can either contain a single LinkTree, or a Header and a LinkTree.
    """

    next_modules = m_leaf + [Footer_Links]

    def match(elements, param, save, env):
        if len(elements) < 1:
            return -1, 0
        e0 = elements[0]
        if "link-list" in e0.e_class:
            return 1, 1
        return -1, 0

    def process_modules(self):
        self.add_class("py-8")
       

    # def analyze(self):
    #     self.modules = [self.module_links]
    #     return super().analyze()

    def render_str(self):
        content = "".join(m.render_str() for m in self.modules)
        return render_m_html(self, "div", content)

    def __str__(self):
        cols = self.param.get("cols", 1)
        return f"<div class='link-list col-{cols}'>{self.module_header}{self.module_links}</div>"


class Footer_LinkTree(RowModule, BranchModule):
    """
    ModuleFooterLinkTree is a container for LinkModules.
    Each LinkModule is a list of links of varying sizes.
    """

    next_modules = [Footer_LinkList] + m_required

    def match(elements, param, save, env):
        if "link-tree" in elements[0].e_class:
            return 2, 1
        return -1, 0
    
    def process_elements(self):
        self.child_env["div_width"] = self.env["div_width"] // 4


    def process_modules(self):

        # heights = [1 for m in self.modules]

        # max_height = max(heights)
        # min_height = min(heights)
        # variance = (max_height - min_height) / max_height

        # The only exception is when the variance is less than 0.8, it is better to
        # if variance < 0.8:
        #     self.param["cols"] = 5
        #     for i in range(len(self.modules)):
        #         self.select_param[i].update({"max_height": max_size, "cols": 1})

        # Try to find the most optimal way to stack the lists.
        sizes =  [[m.get_height()] for m in self.modules[:-1]]

        def update_lists(l):
            print(l)
            l = l.copy()

            min_size = min(sum(i) for i in l)
            smallest_index = [i for i, j in enumerate(l) if sum(j) == min_size][0]
            if smallest_index == 0:
                i = l.pop(0)
                l[0] = i + l[0]
            elif smallest_index == len(l) - 1:
                i = l.pop()
                l[-1] = l[-1] + i
            else:
                prev_height = sum(l[smallest_index - 1])
                next_height = sum(l[smallest_index + 1])
                if prev_height < next_height:
                    l[smallest_index - 1] = l[smallest_index - 1] + l[smallest_index]
                else:
                    l[smallest_index + 1] = l[smallest_index] + l[smallest_index + 1]
                l.pop(smallest_index)
            # smallest_list = l.pop(smallest_index)
            # new_min = min(sum(i) for i in l)
            # second_smallest_index = [i for i, j in enumerate(l) if sum(j) == new_min][0]
            # l[second_smallest_index].extend(smallest_list)

            return l

        def score(l):
            max_size = max(sum(i) for i in l)
            min_size = min(sum(i) for i in l)
            return sum(max_size - sum(i) for i in l)


        best_score = score(sizes)
        # Limit the max height of a single column to prevent all lists stacking into a single column. 
        avg_height = sum(sum(i) for i in sizes) / len(sizes)
        height_limit = avg_height * 2.5
        while True:
            new_sizes = update_lists(sizes)
            new_score = score(new_sizes)
            # total_sizes = [sum(i) for i in new_sizes]
            # avg_size = sum(total_sizes) / len(total_sizes)
            # variance = sum(abs(sz - avg_size) for sz in total_sizes) / len(total_sizes)

            tallest_size = max(sum(i) for i in new_sizes)
           
            print(new_score, best_score)
            if (
                new_score < best_score
                and len(new_sizes) > 1
                and tallest_size < height_limit
            ):
                sizes = new_sizes
                best_score = new_score
            else:
                break

        #raise Exception(sizes)

        cols = len(sizes)
        cols = min(cols, 4)
        self.param["cols"] = cols
        self.add_class(f"basis-{cols}/4")
        self.add_class(f"grid grid-cols-{cols} gap-6")
        # for i, m in enumerate(self.modules):
        #     self.select_param[i].update({"max_height": sizes[i][0], "cols": cols})

        group_class = strings_to_classes(["M_GroupGeneral"])[0]

        new_modules = []
        for i in sizes:
            new_modules.append(group_class([], self.param, self.env))
            for j in i:
                new_modules[-1].modules.append(self.modules.pop(0))
            
        self.modules = new_modules

        # for m in self.modules:
        #     m.add_class(f"py-4")


    # def lists_4(self):
    #     sizes = [[len(m.module_links.modules)] for m in self.modules]

    #     def update_lists(l):
    #         print(l)
    #         l = l.copy()
    #         max_size = max(max(i) for i in l)
    #         min_size = min(min(i) for i in l)
    #         variance = (max_size - min_size) / max_size
    #         if variance < 0.8:
    #             return None

    #         max_indexes = [i for i, j in enumerate(sizes) if max(j) == max_size]
    #         max_lists = [l[i] for i in max_indexes]
    #         for max_list in max_lists:
    #             if len(max_list) == 1 or max(max_list) - min(max_list) < 1:
    #                 max_list.append(0)
    #             for m in range(len(max_list) - 1):
    #                 max_list[m] -= 1
    #                 max_list[-1] += 1
    #         return l

    #     while True:
    #         new_sizes = update_lists(sizes)
    #         if new_sizes is None:
    #             break
    #         sizes = new_sizes

    #     max_sizes = [max(i) for i in sizes]
    #     col_sizes = [len(i) for i in sizes]

    #     cols = sum(len(i) for i in sizes)
    #     self.param["cols"] = min(cols, 4)

    #     for i in range(len(self.modules)):
    #         self.select_param[i].update(
    #             {"max_height": max_sizes[i], "cols": col_sizes[i]}
    #         )

    def render_str(self):
        return render_branch_m_html(self, "div")


# class NoMisc_SmallLeftovers(SubModule):
#     """
#     This is a submodule of FullLinkTree, so modules like Social Media and Logo
#     have not been processed yet. Misc module may be unprocessed as well if it is small.
#     If the combined size of Logo, Copyright, Social Media, and Misc (if they exist) is small,
#     display them as inline elements.
#     """

#     def match(module, ctx=None):
#         logo = module.param.get("logo", None)
#         c_right = module.param.get("copyright", None)
#         social_media = module.param.get("social_media", None)
#         misc = module.param.get("misc", None)

#         a = logo.info["size"] if logo else 0
#         b = c_right.info["size"] if c_right else 0
#         c = social_media.info["size"] if social_media else 0
#         d = misc.info["size"] if misc else 0

#         if a + b + c + d < 300:
#             return 1

#         return -1

#     def __str__(self) -> str:
#         module_render = []
#         logo = self.param.get("logo", None)
#         if logo:
#             module_render.append(str(logo))
#         c_right = self.param.get("copyright", None)
#         if c_right:
#             module_render.append(str(c_right))
#         social = self.param.get("social_media", None)
#         if social:
#             module_render.append(str(social))
#         misc = self.param.get("misc", None)
#         if misc:
#             module_render.append(str(misc))
#         return "<div class='inline'>" + "".join(module_render) + "</div>"


# class NoMisc_LargeLeftovers(SubModule):
#     """ """

#     def match(module, ctx=None):
#         logo = module.param.get("logo", None)
#         c_right = module.param.get("copyright", None)
#         social_media = module.param.get("social_media", None)
#         misc = module.param.get("misc", None)

#         a = logo.info["size"] if logo else 0
#         b = c_right.info["size"] if c_right else 0
#         c = social_media.info["size"] if social_media else 0
#         d = misc.info["size"] if misc else 0

#         #print(a, b, c, d)
#         if a + b + c + d >= 300:
#             return 1
#         return -1

#     def __str__(self) -> str:
#         raise NotImplementedError()


# class FullLinkTree_NoMisc(SubModule):
#     """
#     Handle cases where there is no Misc module, either because
#     there was none to begin with, or it has already been handled.
#     """

#     sub_modules = [NoMisc_SmallLeftovers, NoMisc_LargeLeftovers]

#     def match(module, ctx=None):
#         p = module.param
#         p = p.get("misc", None)
#         if p is None:
#             return 1
#         # Return 0 in case it id called after Misc module
#         return 0

    # def __str__(self) -> str:
    #     logo = self.param["logo"]
    #     social = self.param["social_media"]
    #     module_render = []
    #     module_render.append(str(logo))
    #     module_render.append(str(social))
    #     #module_render.extend([str(m) for m in self.param["modules"]])
    #     #print([m.__class__ for m in self.param["modules"]])
    #     return "".join(module_render)


# class Misc_LargeMisc(SubModule):

#     sub_modules = [FullLinkTree_NoMisc]

#     def match(module, ctx=None):
#         misc = module.param["misc"]
#         if misc.info["size"] > 500:
#             misc.param.update({"misc": None})
#             return 1
#         return -1

#     def __str__(self) -> str:
#         misc = self.param["misc"]
#         misc.param["width"] = 4
#         misc_s = str(misc)
#         return misc_s + str(self.sub_module)


# class Misc_SmallMisc(SubModule):

#     sub_modules = [FullLinkTree_NoMisc]

#     def match(module, ctx=None):
#         misc = module.param["misc"]
#         if misc.info["size"] <= 500:
#             misc.param.update({"misc": None})
#             return 1
#         return -1

#     def __str__(self) -> str:
#         misc = self.param["misc"]
#         misc.param["width"] = 1
#         # misc_s = str(misc)
#         return str(self.sub_module)  # + misc_s


# class FullLinkTree_Misc(Module):
#     """
#     If the Link Tree spans the entire page,
#     misc elements must be placed below the link tree.
#     It should either be:
#     - Tucked away in the bottom right as inline elements if they are small leafs (cloud.google.com)
#     - Also span the whole page as block elements if they are large or are groups (www.netlify.com)
#     """

#     sub_modules = [
#         Misc_LargeMisc,
#         Misc_SmallMisc,
#     ]

#     def match(module, ctx=None):
#         p = module.param
#         p = p.get("misc", None)
#         if p is None:
#             return -1
#         return 1


# class ModuleFooter_FullLinkTree(BranchModule):

#     # sub_modules = [
#     #     ModuleFooter_NoLinkTree
#     # ]

#     def match(elements, param, save, env):
#         if elements[0].e_class == "link-tree":
#             return 1, 1
#         return -1, 0

#     def __str__(self) -> str:
#         return ""
    
#     def render_str(self):
#         return ""


# class ModuleFooter_PartialLinkTree(Module):

#     # sub_modules = [
#     #     PartialLinkTree_Misc,
#     #     PartialLinkTree_NoMisc,
#     # ]

#     def match(module, ctx=None):
#         p = module.param
#         p = p.get("link_tree", None)
#         if p is None:
#             return -1
#         if p.param["cols"] < 4:
#             return 1
#         else:
#             return -1

#     def process_modules(self):
#         pass
#         # TODO: Put Misc or logo+social_media+copyright in CompactGroup

#     # def __str__(self) -> str:
#     #     lt = self.param["link_tree"]
#     #     lt_s = str(lt)
#     #     s = str(self.sub_module)
#     #     return lt_s + s


# class ModuleFooter_NoLinkTree(Module):
#     def match(module, ctx=None):
#         p = module.param
#         p = p.get("link_tree", None)
#         if p is None:
#             return 1
#         return -1

#     def __str__(self) -> str:
#         module_render = []
#         logo = self.param["logo"]
#         module_render.append(str(logo))
#         module_render.extend([str(m) for m in self.param["modules"]])
#         return "".join(module_render)


class M_Footer(VarModule, BranchModule):
    """
    ModuleFooter is essentially identical to ModuleGroupSection,
    with specific optimizations for footer layout.

    ModuleFooter can contain one or more of the following submodules:
    - ModuleFooterLinkTree
    - ModuleTitle
    - ModuleSocialMedia
    - ModuleElements
    - ModuleMisc
    - ModuleCopyright

    """

    next_modules = [
        "Footer_LinkTree",
    ] + starter_modules

    # sub_modules = [
    #     "ModuleFooter_FullLinkTree",
    #     "ModuleFooter_PartialLinkTree",
    #     "ModuleFooter_NoLinkTree",
    # ]

    def match(elements, param, save, env):
        if len(elements) < 1:
            return (-1, 1)
        e0 = elements[0]
        if e0.e_tag == "footer":
            return (1, 1)
        return (-1, 1)
    
    def process_elements(self):
        self.param["cols"] = 1

    # def process_modules(self):
    #     # Find the link tree
    #     link_tree = [m for m in self.modules if m.m_class == "link-tree"]
    #     m = link_tree[0] if link_tree else None
    #     self.param["link_tree"] = m

    #     # Find the Logo module
    #     logo = [m for m in self.modules if m.m_class == "logo"]
    #     m = logo[0] if logo else None
    #     self.param["logo"] = m

    #     # Find the Social Media module
    #     social_media = [m for m in self.modules if m.m_class == "social-media"]
    #     m = social_media[0] if social_media else None
    #     self.param["social_media"] = m

    #     # Find the Misc module
    #     misc = [m for m in self.modules if m.m_class == "misc"]
    #     m = misc[0] if misc else None
    #     self.param["misc"] = m

    def __str__(self) -> str:
        s = str(self.sub_module)
        return "<footer>" + s + "</footer>"
    
    def render_str(self):
        module_render = [m.render_str() for m in self.modules]
        return (
            "<footer class='py-20'><div class='mx-auto w-[1080px] flex flex-wrap'>"
            + "".join(module_render)
            + "</div></footer>"
        )
