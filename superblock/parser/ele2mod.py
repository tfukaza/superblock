import modules
from util import ID_Gen_ThreadSafe, strings_to_classes
from module_list import *

from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel


class ElementToModule:

    # modules = (
    #     [
    #         M_Body,
    #         M_Section,
    #     ]
    #     + branches
    #     + leaf_modules
    # )

    def __init__(
        self,
    ):
        pass

    def parse_start(self, element):
        param = {
            "self": None,
            "class": None,
            "parent": None,
            "children": [],
        }
        d = {
            "div_width": 72,  # Width of current container
            "x_start": 0,  # Start of current container
            "x_current": 0,  # Current x position
            "y_start": 0,  # Start of current container
            "y_current": 0,  # Current y axis position
            "font-size": 2,
            "direction": "column",
            "id_gen": ID_Gen_ThreadSafe(),
            "debug_console": Console(),
            "rich_tree": Tree(
                "Modules",
                guide_style="bright_blue",
                )
            
        }
        sm = strings_to_classes(starter_modules)
        modules = self.parse([element], param, sm, d)
        modules[0]._post_process()
        modules[0].submodule_match()
        return modules[0]

    def update_env(self, env, param, module):
        # c_width = env["div_width"]
        # x_start = env["x_start"]
        # x_current = env["x_current"]
        # y_start = env["y_start"]
        # y_current = env["y_current"]
        direction = env["direction"]

        m_width = module.get_width()
        m_height = module.get_height()

        if direction == "column":
            env["y_current"] += m_height
        elif direction == "row":
            env["x_current"] += m_width
        elif direction == "var":
            module_index = param["module_index"]
            cols = param["cols"]
            if (module_index + 1) % cols == 0:
                env["y_current"] += m_height
                env["x_current"] = 0
            else:
                env["x_current"] += m_width

    def parse(self, elements, params, mods, env):
        """
        Given a list of elements, return a list of modules.
        """
        modules = []
        env = env.copy()
        env["parser"] = self.parse
        env["x_start"] = env.get("x_current", 0)
        env["y_start"] = env.get("y_current", 0)
        params["module_index"] = 0

        rich_tree = env["rich_tree"]

        i = 0
        while i < len(elements):
            # time.sleep(0.1)
            # print("parsing", elements[i:])
            params["parsed_elements"] = elements[:i]
            saves = [{} for _ in range(len(mods))]
            score_count = [
                m.match(elements[i:], params, s, env) for m, s in zip(mods, saves)
            ]
            # print([(s, m) for s, m in zip(mods, score_count)])
            scores = [s[0] for s in score_count]
            counts = [s[1] for s in score_count]
            # print(scores)

            if max(scores) == -1:
                raise Exception("No module found for elements: " + str(elements[i:]))

            highest_index = 0
            m_s = max(score_count)
            for s in score_count:
                if s[0] == m_s[0] and s[1] == m_s[1]:
                    break
                highest_index += 1
            best_module = mods[highest_index]
            module_len = counts[highest_index]

            is_module_leaf = best_module.is_leaf()
            selected_elements = elements[i : i + module_len]

            m = best_module(selected_elements, params, env)
            m.update_param(saves[highest_index])
            m.param["prev"] = modules[-1] if modules else None
            if modules:
                modules[-1].param["next"] = m

            #if env.get("search", 0) < 1:
            m.child_env["rich_tree"] = rich_tree.add(f"{module_len} {best_module} {m.param['m_id']}")
            # else:
            #     m.child_env["rich_tree"] = rich_tree.add(Panel.fit("Hello, [red]World!"))

            #print(f"{'  ' * env.get('depth', 0)}Match: {module_len} {best_module} {m.param['m_id']+1}") 

            if is_module_leaf:
                if len(selected_elements) > 1:
                    raise Exception("Leaf Modules cannot have more than one element")
                m.process_modules()
                m.analyze()
            else:
                m.module_parse(self.parse)
            modules.append(m)

            i += module_len
            params["module_index"] += 1
            self.update_env(env, params, m)


        # if len(modules) > 1:
        #     modules = [[m] for m in modules if not isinstance(m, list)]
        # print("Returning", modules)

        # return modules
        return modules or []
        # else:

        #     return [ModuleGroupGeneral([[m] for m in modules])]
