import numpy as np
from xml_parser import XmlParser
from shape_render import ShapeRender

if __name__ == '__main__':
    file_name = './input_data/sample_input.xml'
    xml_parser = XmlParser()
    shape_renderer = ShapeRender()

    shapes = xml_parser.parse_file(file_name)

    shape_renderer.render_shapes(shapes)