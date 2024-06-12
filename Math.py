from __future__ import annotations
import math

# Sorry I just dont like numpy vectors
class Vector2():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def __repr__(self):
        return "Vector2: " + str(self.x) + ", " + str(self.y)

    def __add__(self, v: Vector2):
        return Vector2(self.x + v.x, self.y + v.y)
    def __sub__(self, v: Vector2):
        return Vector2(self.x - v.x, self.y - v.y)
    def dot(self, v: Vector2) -> float:
        return (self.x * v.x) + (self.y * v.y)
    def __mul__(self, s: float):
        return Vector2(self.x * s, self.y * s)
    def magnitude(self) -> float:
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    # Find closest point to this point on a line
    # defined by two other points
    def closest_point_on_line(self, p1: Vector2, p2: Vector2) -> Vector2:
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x0, y0 = self.x, self.y

        m = (y2-y1)/(x2-x1)
        b = y1 - (m*x1)
        m_prime = -(1/m)
        b_prime = y0 - (m_prime * x0)

        x_star = (b_prime - b) / (m - m_prime)
        y_star = (m * x_star) + b 

        return Vector2(x_star, y_star)

    # Find closest point to this point on a bounded line segment
    # defined by two other points
    def closest_point_on_line_segment(self, p1: Vector2, p2: Vector2) -> Vector2:
        line_vector = p2 - p1
        point_vector = self - p1
        
        projection = point_vector.dot(line_vector) / line_vector.dot(line_vector)
        projection = max(0, min(1, projection))
        
        return p1 + (line_vector * projection)
    
    def closest_point_on_curve(self, curve: Curve) -> Vector2:
        # Iterate through all line segments in the curve
        best_point = Vector2(0, 0)
        best_perp_dist = math.inf
        for i, p in enumerate(curve.points):
            if i == len(curve.points) - 1:
                break

            next_point = Vector2(curve.points[i+1].x, curve.points[i+1].y)

            # Find closest point for this segment
            closest_point = self.closest_point_on_line_segment(p, next_point)
            perp_dist = (closest_point - self).magnitude()

            if perp_dist < best_perp_dist:
                best_perp_dist = perp_dist
                best_point = closest_point
        
        return best_point
    
    def project_onto_line(self, p1: Vector2, p2: Vector2) -> float:
        proj_point = self.closest_point_on_line(p1, p2)
        proj_dist = (p1 - proj_point).magnitude()

        # find sign of this distance
        line_vector = p1 - p2
        displacement_vector = p1 - proj_point

        if (line_vector.dot(displacement_vector) < 0):
            proj_dist = -proj_dist

        return proj_dist

class Curve():
    # Curve points are just (x, y) tuples
    def __init__(self, points: list[Vector2]):
        self.points = points