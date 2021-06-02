import xml.etree.ElementTree as ET

shape_types = ['Quadrilateral', 'Circle', 'Line', 'Triangle', 'Composite']


class XmlParser:

    def parse_file(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        shapes = []
        for child in root:
            shape = self.parse_shape(child)
            shapes.append(shape)
        return shapes

    def parse_shape(self, element):
        shape = element.attrib
        shape['Type'] = element.tag
        sub_elements = element.getchildren()
        if len(sub_elements) > 0:
            shape['Sub Shapes'] = [self.parse_shape(sub_element) for sub_element in sub_elements]
        return shape
