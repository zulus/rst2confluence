from docutils import nodes, writers

import sys

class Writer(writers.Writer):
    def translate(self):
        self.visitor = ConfluenceTranslator(self.document)
        self.document.walkabout(self.visitor)
        self.output = self.visitor.astext()


class ConfluenceTranslator(nodes.NodeVisitor):
    """Write output in Confluence Wiki format.

    References:
    * ReST: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
    * Confluence Wiki: http://confluence.atlassian.com/renderer/notationhelp.action
    """

    empty_methods = [
        'visit_document', 'depart_document',
        'depart_Text',
        'depart_list_item',
        'visit_target', 'depart_target',
        'depart_field_list',
        'visit_field', 'depart_field',
        'depart_field_body',
        'visit_decoration', 'depart_decoration',
        'depart_footer',
        'visit_block_quote', 'depart_block_quote',
        'visit_tgroup', 'depart_tgroup',
        'visit_colspec', 'depart_colspec',
        'depart_image',
    ]

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = document.settings

        self.content = []

        self.first = True
        self.list_level = 0
        self.section_level = 0
        self.list_counter = -1

        self.list_prefix = []

        # Block all output
        self.block = False

        for method in self.empty_methods:
            setattr(self, method, lambda n: None)

    def _add(self, string):
        if not self.block:
            self.content.append(string)

    def _indent(self):
        self._add(" " * self.list_level * 2)

    def _newline(self, number=1):
        self._add("\n"*number)

    def astext(self):
        return ''.join(self.content)

    def unknown_visit(self, node):
        raise Exception("Unknown visit on line %s: %s." % (node.line, repr(node)))

    def unknown_departure(self, node):
        raise Exception("Unknown departure on line %s: %s." % (node.line, repr(node)))


    def visit_paragraph(self, node):
        if not self.first:
            self._newline()

    def depart_paragraph(self, node):
        self._newline()
        self.first = False

    def visit_Text(self, node):
        string = node.astext()
        self._add(string)

    def visit_emphasis(self, node):
        pass

    def depart_emphasis(self, node):
        pass

    def visit_strong(self, node):
        pass

    def depart_strong(self, node):
        pass

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_reference(self, node):
        pass

    def depart_reference(self, node):
        pass

    def visit_literal_block(self, node):
        pass

    def depart_literal_block(self, node):
        pass

    def visit_literal(self, node):
        pass

    def depart_literal(self, node):
        pass

    def visit_footer(self, node):
        pass

    #----------------------------------------------------

    # title
    def visit_title(self, node):
        if not self.first:
            self._newline()
        self._add("h" + str(self.section_level) + ".")

    def depart_title(self, node):
        self._newline(2)
        self.first = True

    def visit_subtitle(self,node):
        self.title_level += 1
        self._add("h" + str(self.section_level) + ".")

    def depart_subtitle(self,node):
        self._newline(2)

    # bullet list
    def visit_bullet_list(self, node):
        self.list_level += 1
        self.list_prefix.append("*")

    def depart_bullet_list(self, node):
        self.list_level -= 1
        self.list_prefix.pop()

    def visit_list_item(self, node):
        self._add("".join(self.list_prefix) + " ")
        self.first = True

    # enumerated list
    def visit_enumerated_list(self, node):
        self.list_prefix.append("#")
        self.list_counter = 1
        self.list_level += 1

        sys.stderr.write("start bullet list:" + str(self.list_level) + "\n")

    def depart_enumerated_list(self, node):
        self.list_counter = -1
        self.list_level -= 1
        self.list_prefix.pop()

    # paragraph
    def visit_note(self, node):
        self._add("{note}")
        self._newline()

    def depart_note(self, node):
        self._add("{note}")
        self._newline(2)

    def visit_warning(self, node):
        self._add("{warning}")

    def depart_warning(self, node):
        self._add("{warning}")
        self._newline(2)

    # image
    def visit_image(self, node):
        uri = node['uri']
        atts = {}
        if 'alt' in node:
            atts['alt'] = node['alt']
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'align' in node:
            atts['align'] = node['align']
        attributes = []
        for att in atts.iterkeys():
            attributes.append(att + "=" + atts[att])

        self._add("!")
        self._add(uri)
        if attributes:
            self._add("|")
            self._add(",".join(attributes))
        self._add("!")

    def visit_table(self, node):
        sys.stderr.write("start table\n")

    def depart_table(self, node):
        sys.stderr.write("end table\n")

    def visit_thead(self, node):
        self._add("||")

    def depart_thead(self, node):
        self._add("||")

    def visit_tbody(self, node):
        sys.stderr.write("")

    def depart_tbody(self, node):
        sys.stderr.write("")

    def visit_row(self, node):
        self._add("|")

    def depart_row(self, node):
        self._add("|")

    def visit_entry(self, node):
        sys.stderr.write("")

    def depart_entry(self, node):
        sys.stderr.write("")