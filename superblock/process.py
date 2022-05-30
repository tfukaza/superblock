from util import *

def e_until_next_hr(elements):
    """
    Returns a list of elements until the next hr,
    and elements after the hr.
    """
    list_1, list_2 = [], elements.copy()
    for e in elements:
        if e.e_tag == "hr":
            return list_1, list_2[1:]
        list_1.append(e)
        list_2.remove(e)
    return list_1, list_2[1:]


def e_until_next_vr(elements):
    """
    Returns a list of elements until the next vr.
    """
    e_list = []
    for e in elements:
        if e.e_tag == "vr":
            return e_list
        e_list.append(e)
    return e_list

def e_list_has_tag(elements, tag):
    for e in elements:
        if e.e_tag == tag:
            return True
    return False

def m_check_center_align(module):
    """
    Checks if a module needs to be centered.
    This applies to TextGroup modules which 
    - is followed by a module that does not span the entire width of the screen
    - section only has texts that do not span the entire width of the screen

    """
    pass

def m_add_margins(modules, related=8, different=12, ex=8):
    if modules is None:
        return
    prev_main_type = modules[0].m_main_type
    extra = 0
    for m in modules[1:]:
        if prev_main_type == e_type.DIVIDER:
            extra = ex

        if m.m_main_type != prev_main_type:
            m.add_class(f"mt-{different + extra}")
        else:
            m.add_class(f"mt-{related + extra}")
        extra = 0
        prev_main_type = m.m_main_type

def m_group_horizontal_compact(module):
    """
    Takes a branch module m.
    If all child modules in m does not have a width of 'full' - 
    that is, none of them span the entire width of the container - 
    then the width of m and its children will be adjusted so 
    the width of m is the same as the widest child module while retaining 
    the current layout. 

    For now, only width of paragraphs are considered. 
    """
    mods = module.modules 
    c_w = module.env["div_width"]
    if len(mods) == 0:
        return
    widths = []
    for m in mods:
        if m.m_type != e_type.PARAGRAPH:
            # widths.append(-1)
            pass
        if m.has_attr("w"):
            w = m.get_attr("w")
            if w == "w-full":
                return
            w = tw_w_to_float(w[2:])
            w = w * c_w
            widths.append(w)
        else:
            # Note that paragraphs ay return values greater than 72
            # but that's okay, since tw_w_to_float will max out at 1 anyways. 
            widths.append(m.get_width(contain=True))
    if len(widths) == 0:
        return
    max_w = max(widths)
    max_tw_w = tw_float_to_w(max_w / c_w)
    tw_w = f"w-{max_tw_w}"
    
    module.remove_attr("w")
    module.add_class(tw_w)

    for m in mods:
        if m.has_attr("w"):
            w = m.get_attr("w")
            w = tw_w_to_float(w[2:])
            w = w * c_w
            w = w / max_w
            w = tw_float_to_w(w, True)
            w = f"w-{w}"
            m.remove_attr("w")
            m.add_class(w)
        


