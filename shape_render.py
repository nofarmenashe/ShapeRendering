import cv2 as cv
import numpy as np
from matplotlib import colors
IMAGE_SIZE = 500

ShapeTypes = ['Quadrilateral', 'Circle', 'Line', 'Triangle', 'Composite']


class ShapeRender:
    def __init__(self):
        self.defined_shapes = {}

    def render_shapes(self, shapes):
        img = self.create_blank_canvas()
        img.fill(255)
        for shape in shapes:
            self.add_shape_to_canvas(shape, img)

        cv.imshow('dark', img)

        cv.waitKey(0)
        cv.destroyAllWindows()

    def add_shape_to_canvas(self, shape, canvas):
        shape_image = self.create_blank_canvas()

        if shape['Type'] == 'Composite':
            for sub_shape in shape['Sub Shapes']:
                self.add_shape_to_canvas(sub_shape, shape_image)
            self.defined_shapes[shape['Name']] = shape_image
            return

        shape_image = self.get_basic_shape(shape, shape_image)

        rotate, scale, translate_x, translate_y = self.extract_transformation_params(shape)
        if rotate != 0 or scale != 1.0 or translate_x != 0 or translate_y != 0:
            shape_image = self.transform_image(shape_image, rotate, scale, translate_x, translate_y)

        cv.imshow(str(scale), shape_image)

        shape_image = shape_image[:IMAGE_SIZE, :IMAGE_SIZE, :]
        indices = np.where(np.any(~np.isnan(shape_image), axis=-1))
        canvas[indices] = shape_image[indices]

    def get_basic_shape(self, shape, shape_image):
        if shape['Type'] == 'Circle':
            self.draw_circle(shape_image, shape)

        elif shape['Type'] == 'Triangle' or shape['Type'] == 'Line' or shape['Type'] == 'Quadrilateral':
            self.draw_Shape_based_on_points(shape['Sub Shapes'], shape_image, shape['Color'], shape.get('FillingColor'))

        else:
            shape_image = self.defined_shapes[shape['Type']]
        return shape_image

    def create_blank_canvas(self):
        composite_img = np.empty((IMAGE_SIZE, IMAGE_SIZE, 3), dtype="uint8") * np.nan
        return composite_img

    def extract_transformation_params(self, shape):
        rotate = int(shape['Rotate']) if 'Rotate' in shape.keys() else 0
        scale = float(shape['Scale']) if 'Scale' in shape.keys() else 1.0
        translate_x = int(shape['TranslateX']) if 'TranslateX' in shape.keys() else 0
        translate_y = int(shape['TranslateY']) if 'TranslateY' in shape.keys() else 0
        return rotate, scale, translate_x, translate_y

    def transform_image(self, img, rotate, scale, translate_x, translate_y):
        indices = np.where(np.any(~np.isnan(img), axis=-1))
        img = img[indices[0].min():indices[0].max(), indices[1].min():indices[1].max(), :]
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        rotation_matrix = cv.getRotationMatrix2D((cX, cY), rotate, scale)

        shift_matrix = np.float32([[1, 0, translate_x], [0, 1, translate_y]])
        rotation_matrix = np.vstack([rotation_matrix, [0, 0, 1]])
        transformation_matrix = np.matmul(shift_matrix, rotation_matrix)

        # img = cv.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv.INTER_AREA)
        return cv.warpAffine(img, transformation_matrix, (IMAGE_SIZE, IMAGE_SIZE),
                              borderMode=cv.BORDER_CONSTANT,
                              borderValue=(np.nan, np.nan, np.nan))

    def draw_circle(self, img, shape):
        center = (int(shape['X']), int(shape['Y']))
        radius = int(shape['Radius'])
        if 'FillingColor' in shape.keys():
            cv.circle(img, center, radius, self.color_to_bgr(shape['FillingColor']), thickness=-1)
        cv.circle(img, center, radius, self.color_to_bgr(shape['Color']), thickness=4)

    def draw_Shape_based_on_points(self, points_elements, img, color, fill_color=None):
        points = []
        for p in points_elements:
            points.append([int(p['X']), int(p['Y'])])
        points = [np.array(points, dtype=np.int32)]
        cv.polylines(img, points, isClosed=True, color=self.color_to_bgr(color), thickness=4)

        if fill_color is not None:
            cv.fillPoly(img, points, color=self.color_to_bgr(fill_color))

    def color_to_bgr(self, color):
        (r, g, b) = tuple([255*x for x in colors.to_rgb(color)])
        return b, g, r
