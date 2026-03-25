# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: shared\service\collision.py
"""
Created on Nov 23, 2019

@author: Admin
"""

def are_polygons_intersecting(poly_a, poly_b) -> bool:
    """
    Return True if two polygons intersect.
    :param PointList poly_a: List of points that define the first polygon.
    :param PointList poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect
    :rtype bool:
    """
    for polygon in (poly_a, poly_b):
        for i1 in range(4):
            i2 = (i1 + 1) % 4
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]
            normal = (
             projection_2[1] - projection_1[1],
             projection_1[0] - projection_2[0])
            min_a, max_a, min_b, max_b = (None, None, None, None)
            for poly in poly_a:
                projected = normal[0] * poly[0] + normal[1] * poly[1]
                if min_a is None or projected < min_a:
                    min_a = projected
                if max_a is None or projected > max_a:
                    max_a = projected

            for poly in poly_b:
                projected = normal[0] * poly[0] + normal[1] * poly[1]
                if min_b is None or projected < min_b:
                    min_b = projected
                if max_b is None or projected > max_b:
                    max_b = projected

            if max_a <= min_b or max_b <= min_a:
                return False

    return True


def check_for_collision(sprite1, sprite2) -> bool:
    """
    Check for a collision between two sprites.
    :param sprite1: First sprite
    :param sprite2: Second sprite
    :Returns: True or False depending if the sprites intersect.
    """
    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1, sprite2) -> bool:
    """
    Check for collision between two sprites.
    :param Sprite sprite1: Sprite 1
    :param Sprite sprite2: Sprite 2
    :returns: Boolean
    """
    collision_radius_sum = sprite1.collision_radius + sprite2.collision_radius
    diff_x = sprite1.position[0] - sprite2.position[0]
    diff_x2 = diff_x * diff_x
    if diff_x2 > collision_radius_sum * collision_radius_sum:
        return False
    diff_y = sprite1.position[1] - sprite2.position[1]
    diff_y2 = diff_y * diff_y
    if diff_y2 > collision_radius_sum * collision_radius_sum:
        return False
    else:
        distance = diff_x2 + diff_y2
        if distance > collision_radius_sum * collision_radius_sum:
            return False
        return are_polygons_intersecting(sprite1.vertices, sprite2.vertices)


def check_for_collision_with_list(sprite, sprite_list):
    """
    Check for a collision between a sprite, and a list of sprites.
    :param Sprite sprite: Sprite to check
    :param SpriteList sprite_list: SpriteList to check against
    :returns: List of sprites colliding, or an empty list.
    """
    sprite_list_to_check = sprite_list
    collision_list = [sprite2 for sprite2 in sprite_list_to_check if sprite is not sprite2 if _check_for_collision(sprite, sprite2)]
    return collision_list


def is_point_in_polygon(x, y, polygon_point_list):
    """
    Use ray-tracing to see if point is inside a polygon
    Args:
        x:
        y:
        polygon_point_list:
    Returns: bool
    """
    inside = False
    p1x, p1y = polygon_point_list[0]
    for i in range(5):
        p2x, p2y = polygon_point_list[i % 4]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
            p1x, p1y = p2x, p2y

    return inside


def get_sprites_at_point(point, sprite_list):
    """
    Get a list of sprites at a particular point
    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against
    :returns: List of sprites colliding, or an empty list.
    """
    sprite_list_to_check = sprite_list
    collision_list = [sprite2 for sprite2 in sprite_list_to_check if is_point_in_polygon(point[0], point[1], sprite2.points)]
    return collision_list
