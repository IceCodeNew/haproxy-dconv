import re
import parser

# Detect examples blocks
class Parser(parser.Parser):
    def __init__(self, pctxt):
        parser.Parser.__init__(self, pctxt)
        template = pctxt.templates.get_template("parser/example/comment.tpl")
        self.comment = template.render().strip()


    def parse(self, line):
        pctxt = self.pctxt

        result = re.search(r'(Examples? *:)', line)
        if result:
            label = result.group(0)

            desc_indent = False
            desc = re.sub(r'.*Examples? *:', '', line).strip()

            # Some examples have a description
            if desc:
                desc_indent = len(line) - len(desc)

            indent = self.get_indent(line)

            if desc:
                # And some description are on multiple lines
                while pctxt.get_line(1) and self.get_indent(pctxt.get_line(1)) == desc_indent:
                    desc += " " + pctxt.get_line(1).strip()
                    pctxt.next()

            pctxt.next()
            add_empty_line = pctxt.eat_empty_lines()

            content = []

            if self.get_indent(pctxt.get_line()) > indent:
                if desc:
                    desc = desc[0].upper() + desc[1:]
                add_empty_line = 0
                while pctxt.has_more_lines() and ((not pctxt.get_line()) or (self.get_indent(pctxt.get_line()) > indent)):
                    if pctxt.get_line():
                        for j in xrange(0, add_empty_line):
                            content.append("")

                        content.append(re.sub(r'(#.*)$', self.comment, pctxt.get_line()))
                        add_empty_line = 0
                    else:
                        add_empty_line += 1
                    pctxt.next()
            elif self.get_indent(pctxt.get_line()) == indent:
                # Simple example that can't have empty lines
                if add_empty_line:
                    # This means that the example was on the same line as the 'Example' tag
                    content.append(" " * indent + desc)
                    desc = False
                else:
                    while pctxt.has_more_lines() and (self.get_indent(pctxt.get_line()) == indent):
                        content.append(pctxt.get_line())
                        pctxt.next()
                    pctxt.eat_empty_lines() # Skip empty remaining lines

            pctxt.stop = True

            template = pctxt.templates.get_template("parser/example.tpl")
            return template.render(
                label=label,
                desc=desc,
                content=content
            )
        return line
