from elements import *
import bs4
from bs4 import BeautifulSoup


class Id_Generator:
    def __init__(self):
        self.id = 0

    def nxt(self):
        self.id += 1
        return self.id


class HtmlToElementParser:
    def __init__(self) -> None:
        self.id_gen = Id_Generator()

    def parse_start(self, f):
        soup = BeautifulSoup(f, "html.parser")
        stats = {}
        e = ElementGroup(None)
        e.e_tag = "body"
        ele = self.parse(soup, stats)
        e.add_elements(ele)
        e.analyze()
        return e

    def parse(self, nodes, stats):

        elements = []

        for node in nodes.children:

            if isinstance(node, bs4.element.NavigableString):
                continue

            name = node.name
            attrs = node.attrs
            ctx = {k[5:]: v for k, v in attrs.items() if k[:4] == "data"}

            if name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                e = ElementHeader(ctx, text=node.string, level=int(name[1]))
                elements.append(e)
            elif name == "p":
                e = self.create_text_element(ctx, node)
                elements.append(e)
            elif name == "hr":
                e = ElementDivider(ctx)
                elements.append(e)
            elif name == "vr":
                e = E_VerticalDivider(ctx)
                elements.append(e)
            elif name == "img":
                src = attrs.get("src", "")
                e = ElementImage(ctx, src)
                elements.append(e)
            elif name == "video":
                src = attrs.get("src", "")
                e = ElementVideo(ctx, src)
                elements.append(e)
            elif name == "a":
                e = ElementLink(ctx)
                e.text = str(node.string)
                e.href = attrs.get("href", "")
                elements.append(e)
            elif name == "button":
                e = ElementButton(ctx)
                e.text = str(node.string)
                e.href = attrs.get("href", "")
                elements.append(e)
            elif name == "span":
                e = ElementSpan(ctx)
                e.text = str(node.string)
                elements.append(e)
            elif name in ["ol", "ul"]:
                e = ElementList(ctx)
                ele = self.parse(node, stats)
                for i in ele:
                    e.add_element(i)
                elements.append(e)
            elif name == "div":
                e = ElementGroup(ctx)
                ele = self.parse(node, stats)
                e.add_elements(ele)
                elements.append(e)
            elif name in ["section", "footer"]:
                e = ElementGroup(ctx)
                ele = self.parse(node, stats)
                e.add_elements(ele)
                elements.append(e)
            else:
                raise Exception(f"Unrecognized HTML tag {node}")

            e.e_class = attrs.get("class", [])
            e.e_tag = name
            if e.e_tag != "hr":
                e.e_id = self.id_gen.nxt()

        hr = ElementDivider({})
        hr.e_tag = "hr"
        elements.append(hr)

        return elements

    def create_text_element(self, ctx, node):
        # If node has only 1 content, get the string
        # Else, parse the nodes
        if len(node.contents) == 1:
            texts = [("p", str(node.string))]
        else:
            texts = []
            for c in node.contents:
                if isinstance(c, bs4.element.NavigableString):
                    texts.append(("p", str(c)))
                elif c.name == "em":
                    texts.append(("em", str(c.string)))
                else:
                    raise Exception(f"Unrecognized HTML tag {node}")

        return ElementParagraph(ctx, texts)
