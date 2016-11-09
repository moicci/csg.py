# coding: utf-8

import math
from solid import Solid
from csg import CSG

def _create_tri_polygon(solid, i0, i1, i2):
    # CSG.js (WebGL) では時計回りが表
    p0 = solid.vertices[i0]
    p1 = solid.vertices[i1]
    p2 = solid.vertices[i2]
    vertices = []
    vertices.append(CSG.Vector(p0))
    vertices.append(CSG.Vector(p1))
    vertices.append(CSG.Vector(p2))
    return CSG.Polygon(vertices, False)

def _create_tri_polygons(solid, face, color, polygons):
    i0 = face.indices[0]
    for i in xrange(2, len(face.indices) - 1):
        polygon = _create_tri_polygon(solid, i0, face.indices[i - 1], face.indices[i])
        polygon.shared = color
        polygons.append(polygon)

def _create_polygons(solid, face, color, polygons):
    vertices = []
    for i in face.indices[:-1]:
        v = solid.vertices[i]
        vertices.append(CSG.Vector(v))

    polygon = CSG.Polygon(vertices, False)
    polygon.shared = color
    polygons.append(polygon)

def csg_from_solid(solid, as_tri=True):
    as_tri=True # 三角パッチじゃないと、CSG.Node.build で無限ループになってしまう。
    polygons = []
    for f in solid.faces:
        indices = f.indices
        # face は最後が閉じていることに注意
        color = map(lambda c: c / 255.0, f.color) if f.color else None
        if as_tri:
            _create_tri_polygons(solid, f, color, polygons)
        else:
            _create_polygons(solid, f, color, polygons)

    return CSG(polygons)

def csg_to_solid(csg, as_tri=False):
    solid = Solid()
    for p in csg.polygons:
        indices = []
        for v in p.vertices:
            i = solid.append_vertex(v.as_array())
            indices.append(i)

        solid.append_polygon(indices, as_tri=as_tri)
    return solid
