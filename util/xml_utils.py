import xml.etree.ElementTree as ET


def parse_file(path: str) -> ET.Element:
    return ET.parse(path).getroot()


def parse_string(text: str) -> ET.Element:
    return ET.fromstring(text)


def to_string(element: ET.Element, pretty: bool = False, encoding: str = "unicode") -> str:
    if pretty:
        _indent(element)
    return ET.tostring(element, encoding=encoding)


def write_file(element: ET.Element, path: str, pretty: bool = True,
               xml_declaration: bool = True) -> None:
    if pretty:
        _indent(element)
    tree = ET.ElementTree(element)
    tree.write(path, encoding="utf-8", xml_declaration=xml_declaration)


def create_element(tag: str, text: str | None = None, **attrs) -> ET.Element:
    el = ET.Element(tag, {k: str(v) for k, v in attrs.items()})
    if text is not None:
        el.text = str(text)
    return el


def add_child(parent: ET.Element, tag: str, text: str | None = None, **attrs) -> ET.Element:
    child = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
    if text is not None:
        child.text = str(text)
    return child


def remove_child(parent: ET.Element, child: ET.Element) -> None:
    parent.remove(child)


def find(element: ET.Element, path: str) -> ET.Element | None:
    return element.find(path)


def find_all(element: ET.Element, path: str) -> list[ET.Element]:
    return element.findall(path)


def get_attr(element: ET.Element, attr: str, default: str | None = None) -> str | None:
    return element.get(attr, default)


def set_attr(element: ET.Element, attr: str, value: str) -> None:
    element.set(attr, str(value))


def get_text(element: ET.Element | None, default: str = "") -> str:
    if element is None:
        return default
    return (element.text or "").strip() or default


def set_text(element: ET.Element, text: str) -> None:
    element.text = text


def get_all_text(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def element_to_dict(element: ET.Element) -> dict:
    result: dict = {}
    if element.attrib:
        result["@attrs"] = dict(element.attrib)
    if element.text and element.text.strip():
        result["#text"] = element.text.strip()
    for child in element:
        child_dict = element_to_dict(child)
        if child.tag in result:
            existing = result[child.tag]
            if not isinstance(existing, list):
                result[child.tag] = [existing]
            result[child.tag].append(child_dict)
        else:
            result[child.tag] = child_dict
    return result


def dict_to_element(tag: str, data: dict | str | None) -> ET.Element:
    el = ET.Element(tag)
    if isinstance(data, str):
        el.text = data
    elif isinstance(data, dict):
        for k, v in data.items():
            if k == "@attrs":
                for ak, av in v.items():
                    el.set(ak, str(av))
            elif k == "#text":
                el.text = str(v)
            elif isinstance(v, list):
                for item in v:
                    el.append(dict_to_element(k, item))
            else:
                el.append(dict_to_element(k, v))
    return el


def _indent(element: ET.Element, level: int = 0) -> None:
    pad = "\n" + "  " * level
    if len(element):
        if not element.text or not element.text.strip():
            element.text = pad + "  "
        if not element.tail or not element.tail.strip():
            element.tail = pad
        for child in element:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = pad


if __name__ == "__main__":
    xml_str = """<library>
    <book id="1" genre="fiction">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <year>1925</year>
    </book>
    <book id="2" genre="sci-fi">
        <title>Dune</title>
        <author>Frank Herbert</author>
        <year>1965</year>
    </book>
    <book id="3" genre="fiction">
        <title>1984</title>
        <author>George Orwell</author>
        <year>1949</year>
    </book>
</library>"""

    root = parse_string(xml_str)
    print("tag:             ", root.tag)
    print("find('book'):    ", find(root, "book").tag)
    print("find_all books:  ", len(find_all(root, "book")))

    books = find_all(root, "book")
    for book in books:
        print(f"  id={get_attr(book, 'id')} title={get_text(find(book, 'title'))}")

    print("\nadd_child:")
    new_book = add_child(root, "book", id="4", genre="fantasy")
    add_child(new_book, "title", "The Hobbit")
    add_child(new_book, "author", "J.R.R. Tolkien")
    add_child(new_book, "year", "1937")
    print("  books now:", len(find_all(root, "book")))

    print("\nelement_to_dict (first book):")
    import pprint
    pprint.pprint(element_to_dict(books[0]))

    print("\ndict_to_element + to_string:")
    data = {"@attrs": {"id": "5"}, "title": "Test", "author": "Me"}
    el = dict_to_element("book", data)
    print(" ", to_string(el))

    print("\nto_string(pretty=True):")
    mini = parse_string("<root><a>1</a><b>2</b></root>")
    print(to_string(mini, pretty=True))
