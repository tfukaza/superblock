from collections import Counter
from module_list import *
from util import *
from rich.tree import Tree 
from rich.panel import Panel
from rich.columns import Columns


class Module:

    next_modules = (
        None  # List of possible modules that can be applied to the module's elements.
    )
    sub_modules = (
        None  # List of possible sub-modules that can be applied to the module's modules
    )
    # after parsing the elements.
    exclude_modules = None

    passthrough = (
        False  # If True, the module will parse all the elements again instead of
    )
    # parsing each elements individually.

    custom_param = None  # Parameter keys and values specific to the module.

    def __init__(self, elements, p_param, env):
        """
        Initializes required attributes for the module.
        """
        self.param = {
            "self": self,
            "class": self.__class__.__name__,
            "parent": None,
            "children": [""],
            "class_list": [""],
            "m_type": None,
            "m_main_type": None,
            "m_id": env["id_gen"].get_id(),
        }
        self.param["parent"] = p_param
        p_param["children"].append(self.param)

        self.ctx = None
        self.env = {}
        self.child_env = {}
        self._setup_env(env)

        # for e in elements:
        #     print(e.__class__.__name__, self.__class__.__name__)
        #     e.module = self

        if self.custom_param is not None:
            self.param.update(self.custom_param)

        self.elements = elements
        self.modules = None

        self.callbacks = []
        self.sub_module = None

        if self.next_modules is None:
            self.next_modules = starter_modules
        self.next_modules = strings_to_classes(self.next_modules)
        self.exclude_modules = strings_to_classes(self.exclude_modules)
        self.sub_modules = strings_to_classes(self.sub_modules) if self.sub_modules else None
        self.next_modules = [
            m for m in self.next_modules if m not in self.exclude_modules
        ]

    def match(elements, params, save, env):
        """
        Given a list of elements, determines if this module can be applied to 1 or more of the elements.
        If yes, returns a tuple of:
            - A score >= 0, used to evaluate how well the match is
            - An integer > 0, indicating how many elements were matched
        """
        raise NotImplementedError()

    def module_parse(self, parser):
        self._p_e()
        self.process_elements()
        self.element_parse(parser)
        self.analyze()
        self.process_done = True
        self.process_modules()
        self._process_callbacks()
        #self.submodule_match()

    def _p_e(self):
        pass

    def process_elements(self):
        pass

    def passthrough_parse(self, parser):
        m = parser(self.elements, self.param, self.next_modules, self.child_env)
        self.modules.extend(m)

    def element_parse(self, parser):

        if self.passthrough:
            self.passthrough_parse(parser)
            return
        for e in self.elements:
            if is_element_group(e):
                m = parser(e.elements, self.param, self.next_modules, self.child_env)
            else:
                m = parser([e], self.param, self.next_modules, self.child_env)
            self.modules.extend(m)

    # def _remove_dividers(self):
    #     new_mods = [m for m in self.modules if not is_divider(m.e0, 0)]
    #     self.modules = new_mods

    def process_modules(self):
        pass

    def _process_callbacks(self):
        map(lambda r: r[0](*r[1], **r[2]), self.callbacks)
    
    def post_process(self):
        pass 

    def _post_process(self):
        if self.modules is not None:
            for m in self.modules:
                m._post_process()
        self.post_process()

    def submodule_match(self):
        if self.modules is None:
            return  
        for m in self.modules:
            m.submodule_match()

        if self.sub_modules is None:
            return
        scores = [s.match(self, self.param) for s in self.sub_modules]
        best_score = max(scores)
        if best_score < 0.1:
            return
        if best_score < 0:
            raise Exception("No sub-module matched.")
        best_submodule = self.sub_modules[scores.index(best_score)]
        #print(best_submodule)
        self.sub_module = best_submodule(self.elements, self.param)
        self.sub_module.modules = self.modules
        self.sub_module.env = self.env
        self.sub_module.process_modules()
        self.sub_module.submodule_match()


    def analyze(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement analyze()"
        )

    def is_leaf():
        raise NotImplementedError()

    def register_callback(self, callback, args=None, kwargs=None, cls=None):
        self.callbacks.append((callback, args, kwargs))

    def render_str(self):
        raise NotImplementedError(f"{self.__class__} does not implement render")

    def __str__(self) -> str:
        raise NotImplementedError(f"{self.__class__} does not implement __str__")

    def update_param(self, param):
        self.param.update(param)

    def _setup_env(self, env):
        self.env.update(env)
        self.child_env.update(env)
        self.child_env["depth"] = self.env.get("depth", 0) + 1

    def setup_env(self, env):
        pass

    @property
    def parent(self):
        return self.param["parent"]["self"]

    @property
    def e(self):
        return self.elements

    @property
    def e0(self):
        return self.elements[0]

    @property
    def m_main_type(self):
        return self.param["m_main_type"]

    @property
    def m_type(self):
        return self.param["m_type"]

    @property
    def class_list(self):
        return self.param["class_list"]

    @property
    def class_list_str(self):
        return " ".join(self.class_list)
    
    @property
    def m_id(self):
        return self.param["m_id"]

    def add_class(self, cls):
        if " " in cls:
            self.add_classes(cls.split(" "))
        elif cls not in self.class_list:
            self.class_list.append(cls)

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)

    def remove_class(self, cls):
        if cls in self.class_list:
            self.class_list.remove(cls)

    def remove_classes(self, classes):
        for cls in classes:
            self.remove_class(cls)

    def has_class(self, cls):
        return cls in self.class_list

    def has_attr(self, attr):
        attr = f'{attr}-'
        return next(
            ((True, c) for c in self.class_list if c.startswith(attr)),
            (False, None),
        )[0]

    def remove_attr(self, attr):
        attr = f"{attr}-"  
        self.param["class_list"] = list(
            filter(lambda c: not c.startswith(attr), self.class_list)
        )
    
    def get_attr(self, attr):
        attr = f"{attr}-"
        return next(
            (c for c in self.class_list if c.startswith(attr)),
            None,
        )

    def get_width(self, contain=True):
        raise NotImplementedError()

    def get_height(self, contain=True):
        raise NotImplementedError()

    def get_size(self):
        raise NotImplementedError()

    def score(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement score()"
        )


class LeafModule(Module):
    def __init__(self, elements, p_params, env):
        super().__init__(elements, p_params, env)
        self.ctx = self.elements[0].ctx

    def is_leaf():
        return True

    def analyze(self):
        self.param.update(self.e0.info)
        self.param.update(
            {
                "m_type": self.e0.e_type,
                "m_main_type": self.e0.e_type,
            }
        )

    def get_size(self):
        return self.e0.get_size(self.env)

    def get_width(self, contain=True):
        s = self.e0.get_width(self.env)
        return s

    def get_height(self, contain=True):
        return self.e0.get_height(self.env)

    def score(self):
        return -1


class BranchModule(Module):
    def __init__(self, elements, p_params, env):
        super().__init__(elements, p_params, env)
        self.modules = []
    
    
    def search_matches(self, trials, score_self=False):
    
        search = self.env.get("search", 0)
        self.child_env["search"] = search+1
        
        scores = []
        panels = []
        if len(trials) == 1:
            return 0, trials[0], (1, trials[0])
        for trial in trials:
            tmp_p = deepcopy_param(self.param)
            tmp_env = self.env.copy()
            tmp_c_env = self.child_env.copy()
            
            tmp_p.update(trial[0])
            tmp_env.update(trial[1])
            tmp_c_env.update(trial[2])
            tmp_c_env["rich_tree"] = Tree(f"{self.__class__.__name__}")
            score = self.parse_search_tree(
                self.elements, tmp_p, tmp_env, tmp_c_env, score_self
            )
            scores.append(score)
            panels.append(Panel(tmp_c_env["rich_tree"], title=str(trial[0]), subtitle=str(score), expand=False))
        # Find index of best score
        c = Columns()
        for p in panels:
            c.add_renderable(p)
        self.child_env["rich_tree"].add(Panel(c, title="Search", expand=False))
        best_score = max(scores)
        index = scores.index(best_score)
        #For each trial, print the score and the parameters
        #print(f"ID: {self.param['m_id']}")
        # for i, tri in enumerate(trials):
        #     print(f"{tri}: {scores[i]}")
        
        scores_and_trials = list(zip(scores, trials))
        self.child_env["search"] -= 1
        return index, trials[index], scores_and_trials
    


    def parse_search_tree(self, elements, param, env, child_env, score_self=False):
        """
        When called by process_elements(),
        it will create a copy of params and env and then parse them as usual.
        After parsing, it will return the score of the modules.
        """
        # t_param = deepcopy_param(param)
        # env = env.copy()
        # child_env = child_env.copy()
        parser = self.env["parser"]

        save = {}
        self.__class__.match(elements, param, save, env)
        param.update(save)
        self_class = self.__class__
        tmp_self = self_class(self.elements, param, env)
        tmp_self.param = param
        tmp_self.env = env
        tmp_self.child_env = child_env
        tmp_self._p_e()
        # Skip process_elements(), since that is where this
        # function is called from. Otherwise it will cause
        # infinite recursion.
        tmp_self.element_parse(parser)
        tmp_self.analyze()
        tmp_self.process_modules()
        tmp_self._process_callbacks()
        # Skip submodule_match(), since submodukes have no effect on layout.

        if score_self:
            return tmp_self.score()
        scores = [m.score() for m in tmp_self.modules]
        return filter_scores(scores)

    def check_equivalent_group(self):
        self.eq_group = self.is_equivalent_group()
        # if self.eq_group:
        #     # Override info in elements with
        #     pass

    def get_size(self):
        return sum(m.get_size() for m in self.modules)

    def get_width(self, contain=True):
        # if not self.process_done:
        #     print("get_width() called before process_modules()")
        return self.env["div_width"]

    def get_height(self, contain=True):
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement get_height()"
        )

    def score(self):
        scores = [m.score() for m in self.modules]
        #print(f"{self.__class__.__name__}", scores)
        return filter_scores(scores)

    def render_str(self):
        if self.sub_module is None:
            mods = [x.render_str() for x in self.modules]
            return "".join(mods)
        return self.sub_module.render_str()

    def __str__(self):
        if self.sub_module is None:
            mods = [x.__str__() for x in self.modules]
            s = "\n\t".join(mods)
            return f"{self.__class__.__name__}:\n\t{s}"
        return f"{self.__class__.__name__}:\n{self.sub_module.__str__()}"

    def render(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement render"
        )

    def is_leaf():
        return False

    def is_equivalent_group(self):
        """
        Checks if the elements contained in this group have the same structure.
        """
        hashes = [e.get_struct_hash() for e in self.elements]
        return len(hashes) > 1 and len(set(hashes)) == 1

    def analyze(self):
        # child_info = [e.get_info() for e in self.elements]
        sizes = [x.get_size(self.env) for x in self.elements]
        types = [x.e_main_type for x in self.elements]
        freq_type = Counter(types).most_common(1)
        freq_type = freq_type[0][0]

        total_size = sum(sizes)
        avg_size = total_size / len(sizes)
        variance = sum(map(lambda x: ((x - avg_size) ** 2) ** 0.5, sizes)) / len(sizes)

        self.param.update(
            {
                "m_main_type": freq_type,
                "m_type": e_type.GROUP,
                "size": total_size,
                "avg_size": avg_size,
                "variance": variance,
            }
        )

        self.group_analyze()

    def group_analyze(self):
        # for m in self.modules:
        #     pprint(m.param, depth=1)
        # pprint(self.param, depth=1)
        # widths = [x.param["width"] for x in self.modules]
        # heights = [x.param["height"] for x in self.modules]

        self.param.update(
            {
                "width": self.param["size"],
                "height": self.param["size"],
            }
        )


class RowModule(Module):
    def group_analyze(self):
        widths = [m.get_width() for m in self.modules]
        heights = [m.get_height() for m in self.modules]

        self.param.update(
            {
                "width": sum(widths),
                "height": max(heights),
            }
        )

    def get_height(self, contain=True):
        return max(m.get_height() for m in self.modules)

    def _p_e(self):
        self.child_env["direction"] = "row"


class ColumnModule(Module):
    def group_analyze(self):
        widths = [m.get_width() for m in self.modules]
        heights = [m.get_height() for m in self.modules]

        self.param.update(
            {
                "width": max(widths),
                "height": sum(heights),
            }
        )

    def get_height(self, contain=True):
        return sum(m.get_height() for m in self.modules)

    def _p_e(self):
        self.child_env["direction"] = "column"


class VarModule(Module):
    def group_analyze(self):
        cols = self.param["cols"]
        widths = [m.get_width() for m in self.modules]
        widths = [widths[i : i + cols] for i in range(0, len(widths), cols)]
        max_width = max(map(sum, widths))
        heights = [m.get_height() for m in self.modules]
        heights = [heights[i : i + cols] for i in range(0, len(heights), cols)]
        total_height = sum(map(max, heights))

        self.param.update(
            {
                "width": max_width,
                "height": total_height,
            }
        )

    def _p_e(self):
        self.child_env["direction"] = "var"

    def get_height(self, contain=True):
        return self.param["height"]

    def get_width(self, contain=True):
        return self.param["width"]


class SubModule(Module):
    def __init__(self, elements, param):
        self.elements = elements
        self.param = param
        self.callbacks = []
        self.sub_module = None

    def element_parse(self, parser):
        pass

    def render_str(self) -> str:
        if self.sub_module is None:
            raise Exception("Sub-module is expected to be set in default __str__")
        return self.sub_module.render_str()


class BranchSubModule(BranchModule):
    def __init__(self, elements, param):
        self.elements = elements
        self.param = param
        self.callbacks = []
        self.sub_module = None

    def element_parse(self, parser):
        pass

    def render_str(self) -> str:
        if self.sub_module is None:
            raise Exception("Sub-module is expected to be set in default __str__")
        return self.sub_module.render_str()
