# coding:utf-8
import math
import sys


def fp3(value):
    s = "%.3f" % value
    if s == "-0.000":
        return "0.000"
    return s


class CSG:

    def __init__(self, polygons=[]):
        self.polygons = polygons

    @classmethod
    def fromPolygons(cls, polygons):
        return CSG(polygons)

    def clone(self):
        polygons = [p.clone() for p in self.polygons]
        return CSG(polygons)

    def toPolygons(self):
        return self.polygons

    def __str__(self):
        text = ""
        for p in self.polygons:
            text += str(p) + "\n"
        return text

    # Return a new CSG solid representing space in either self solid or in the
    # solid `csg`. Neither self solid nor the solid `csg` are modified.
    #
    #     A.union(B)
    #
    #     +-------+            +-------+
    #     |       |            |       |
    #     |   A   |            |       |
    #     |    +--+----+   =   |       +----+
    #     +----+--+    |       +----+       |
    #          |   B   |            |       |
    #          |       |            |       |
    #          +-------+            +-------+
    #
    def union(self, csg):
        a = CSG.Node(self.clone().polygons)
        b = CSG.Node(csg.clone().polygons)
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons())
        return CSG(a.allPolygons())

    # Return a new CSG solid representing space in self solid but not in the
    # solid `csg`. Neither self solid nor the solid `csg` are modified.
    #
    #     A.subtract(B)
    #
    #     +-------+            +-------+
    #     |       |            |       |
    #     |   A   |            |       |
    #     |    +--+----+   =   |    +--+
    #     +----+--+    |       +----+
    #          |   B   |
    #          |       |
    #          +-------+
    #
    def subtract(self, csg):
        a = CSG.Node(self.clone().polygons)
        b = CSG.Node(csg.clone().polygons)
        a.invert()
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons())
        a.invert()
        return CSG(a.allPolygons())

    # Return a new CSG solid representing space both self solid and in the
    # solid `csg`. Neither self solid nor the solid `csg` are modified.
    #
    #     A.intersect(B)
    #
    #     +-------+
    #     |       |
    #     |   A   |
    #     |    +--+----+   =   +--+
    #     +----+--+    |       +--+
    #          |   B   |
    #          |       |
    #          +-------+
    #
    def intersect(self, csg):
        #print "a-----------"
        a = CSG.Node(self.clone().polygons, name="a")
        #print "b-----------"
        b = CSG.Node(csg.clone().polygons, name="b")
        #print "0: a(%s), b(%s)" % (a.p(), b.p())
        a.invert()
        #print "1: a(%s), b(%s)" % (a.p(), b.p())
        b.clipTo(a)
        #print "2: a(%s), b(%s)" % (a.p(), b.p())
        b.invert()
        #print "3: a(%s), b(%s)" % (a.p(), b.p())
        a.clipTo(b)
        #print "4: a(%s), b(%s)" % (a.p(), b.p())
        b.clipTo(a)
        #print "5: a(%s), b(%s)" % (a.p(), b.p())
        a.build(b.allPolygons())
        #print "6: a(%s), b(%s)" % (a.p(), b.p())
        a.invert()
        #print "7: a(%s), b(%s)" % (a.p(), b.p())
        return CSG(a.allPolygons())

    # Return a new CSG solid with solid and empty space switched. This solid is
    # not modified.
    def inverse(self):
        csg = self.clone()
        [p.flip() for p in csg.polygons]
        return csg

    # # class Vector
    #
    # Represents a 3D vector.
    #
    # Example usage:
    #
    #     new CSG.Vector(1, 2, 3)
    #     new CSG.Vector([1, 2, 3])
    class Vector:

        def __init__(self, x, y=None, z=None):
            if isinstance(x, list):
                self.x = x[0]
                self.y = x[1]
                self.z = x[2]
            else:
                self.x = x
                self.y = y
                self.z = z

        def __str__(self):
            return "[%s, %s, %s]" % (fp3(self.x), fp3(self.y), fp3(self.z))

        def as_array(self):
            return [self.x, self.y, self.z]

        def __getitem__(self, i):
            if i == 0:
                return self.x
            if i == 1:
                return self.y
            if i == 2:
                return self.z
            assert False, "bad index"
            return None

        def clone(self):
            return CSG.Vector(self.x, self.y, self.z)

        def negated(self):
            return CSG.Vector(-self.x, -self.y, -self.z)

        def plus(self, a):
            return CSG.Vector(self.x + a.x, self.y + a.y, self.z + a.z)

        def minus(self, a):
            return CSG.Vector(self.x - a.x, self.y - a.y, self.z - a.z)

        def times(self, a):
            return CSG.Vector(self.x * a, self.y * a, self.z * a)

        def dividedBy(self, a):
            if a == 0.0:
                return self.clone()
            return CSG.Vector(self.x / a, self.y / a, self.z / a)

        def dot(self, a):
            return self.x * a.x + self.y * a.y + self.z * a.z

        def lerp(self, a, t):
            return self.plus(a.minus(self).times(t))

        def length(self):
            return math.sqrt(self.dot(self))

        def unit(self):
            return self.dividedBy(self.length())

        def cross(self, a):
            return CSG.Vector(
                self.y * a.z - self.z * a.y,
                self.z * a.x - self.x * a.z,
                self.x * a.y - self.y * a.x
            )

        # Create a new vertex between self vertex and `other` by linearly
        # interpolating all properties using a parameter of `t`. Subclasses should
        # override self to interpolate additional properties.
        def interpolate(self, other, t):
            return self.lerp(other, t)

    # # class Plane
    #
    # Represents a plane in 3D space.
    #
    # `CSG.Plane.EPSILON` is the tolerance used by `splitPolygon()` to decide if a
    # point is on the plane.
    #Plane_EPSILON = 1e-5
    Plane_EPSILON = 1e-3

    class Plane:

        def __init__(self, normal, w):
            self.normal = normal
            self.w = w

        def __str__(self):
            return str(self.normal) + ", w=" + fp3(self.w)

        @classmethod
        def fromPoints(cls, a, b, c):
            n = b.minus(a).cross(c.minus(a)).unit()
            return CSG.Plane(n, n.dot(a))

        def clone(self):
            return CSG.Plane(self.normal.clone(), self.w)

        def flip(self):
            self.normal = self.normal.negated()
            self.w = -self.w

        # Split `polygon` by self plane if needed, then put the polygon or polygon
        # fragments in the appropriate lists. Coplanar polygons go into either
        # `coplanarFront` or `coplanarBack` depending on their orientation with
        # respect to self plane. Polygons in front or in back of self plane go into
        # either `front` or `back`.
        def splitPolygon(self, polygon, coplanarFront, coplanarBack, front, back):
            COPLANAR = 0
            FRONT = 1
            BACK = 2
            SPANNING = 3

            # Classify each point as well as the entire polygon into one of the above
            # four classes.
            polygonType = 0
            types = []
            for vertex in polygon.vertices:
                t = self.normal.dot(vertex) - self.w
                if t < -CSG.Plane_EPSILON:
                    #print "BACK: t=%.3f" % t
                    typ = BACK
                #else:
                    #typ = FRONT if t > CSG.Plane_EPSILON else COPLANAR
                elif t > CSG.Plane_EPSILON:
                    #print "FRONT: t=%.3f" % t
                    typ = FRONT
                else:
                    #print "COP: t=%.3f" % t
                    typ = COPLANAR

                polygonType |= typ
                types.append(typ)

            # Put the polygon in the correct list, splitting it when necessary.
            if polygonType == COPLANAR:
                if self.normal.dot(polygon.plane.normal) > 0:
                    #print "  COPLANAR: coplanarFront"
                    coplanarFront.append(polygon)
                else:
                    #print "  COPLANAR: coplanarBack"
                    coplanarBack.append(polygon)

            elif polygonType == FRONT:
                #print "  FRONT: front"
                front.append(polygon)

            elif polygonType == BACK:
                #print "  BACK: back"
                back.append(polygon)

            elif polygonType == SPANNING:
                f = []
                b = []
                for i in xrange(len(polygon.vertices)):
                    j = (i + 1) % len(polygon.vertices)
                    ti = types[i]
                    tj = types[j]
                    vi = polygon.vertices[i]
                    vj = polygon.vertices[j]
                    if ti != BACK:
                        f.append(vi)
                    if ti != FRONT:
                        b.append(vi.clone() if not ti == BACK else vi)
                    if (ti | tj) == SPANNING:
                            t = (self.w - self.normal.dot(vi)) / self.normal.dot(vj.minus(vi))
                            v = vi.interpolate(vj, t)
                            f.append(v)
                            b.append(v.clone())

                if len(f) >= 3:
                    #print "  SPANNING: front"
                    front.append(CSG.Polygon(f, polygon.shared))
                if len(b) >= 3:
                    #print "  SPANNING: back"
                    back.append(CSG.Polygon(b, polygon.shared))

    # # class Polygon

    # Represents a convex polygon. The vertices used to initialize a polygon must
    # be coplanar and form a convex loop. They do not have to be `CSG.Vertex`
    # instances but they must behave similarly (duck typing can be used for
    # customization).
    #
    # Each convex polygon has a `shared` property, which is shared between all
    # polygons that are clones of each other or were split from the same polygon.
    # This can be used to define per-polygon properties (such as surface color).
    #
    class Polygon:

        def __init__(self, vertices, shared):
            self.vertices = vertices
            self.shared = shared
            self.plane = CSG.Plane.fromPoints(vertices[0], vertices[1], vertices[2])

        def __str__(self):
            return CSG.Polygon.vertices_to_string(self.vertices)

        @classmethod
        def vertices_to_string(cls, vertices):
            text = ""
            for v in vertices:
                if len(text) > 0:
                    text += " "
                text += str(v)
            return text

        def clone(self):
            vertices = [v.clone() for v in self.vertices]
            return CSG.Polygon(vertices, self.shared)

        def flip(self):
            self.vertices.reverse()
            #[v.flip() for v in self.vertices]
            self.plane.flip()

    # # class Node

    # Holds a node in a BSP tree. A BSP tree is built from a collection of polygons
    # by picking a polygon to split along. That polygon (and all other coplanar
    # polygons) are added directly to that node and the other polygons are added to
    # the front and/or back subtrees. This is not a leafy BSP tree since there is
    # no distinction between internal and leaf nodes.
    class Node:

        def __init__(self, polygons=None, name="Node", level=0):
            self.plane = None
            self.front = None
            self.back = None
            self.name = name
            self.level = level
            self.polygons = []
            if polygons:
                self.build(polygons)

        def clone(self):
            node = CSG.Node()
            if self.plane:
                node.plane = self.plane.clone()
            if self.front:
                node.front = self.front.clone()
            if self.back:
                node.back = self.back.clone()

            node.polygons = [p.clone() for p in self.polygons]
            node.name = self.name
            node.level = self.level
            return node

        # Convert solid space to empty space and empty space to solid space.
        def invert(self):
            for p in self.polygons:
                p.flip()

            if self.plane:
                self.plane.flip()
            if self.front:
                self.front.invert()
            if self.back:
                self.back.invert()

            temp = self.front
            self.front = self.back
            self.back = temp

        # Recursively remove all polygons in `polygons` that are inside self BSP
        # tree.
        def clipPolygons(self, polygons):
            if not self.plane:
                return polygons[:]

            front = []
            back = []

            i = 0
            for p in polygons:
                self.plane.splitPolygon(p, front, back, front, back)
                i += 1

            if self.front:
                front = self.front.clipPolygons(front)
            if self.back:
                back = self.back.clipPolygons(back)
            else:
                back = []

            front.extend(back)
            return front

        # Remove all polygons in self BSP tree that are inside the other BSP tree
        # `bsp`.
        def clipTo(self, bsp):
            self.polygons = bsp.clipPolygons(self.polygons)
            if self.front:
                self.front.clipTo(bsp)
            if self.back:
                self.back.clipTo(bsp)

        # Return a list of all polygons in self BSP tree.
        def allPolygons(self):
            polygons = self.polygons[:]
            if self.front:
                polygons.extend(self.front.allPolygons())
            if self.back:
                polygons.extend(self.back.allPolygons())
            return polygons

        # Build a BSP tree out of `polygons`. When called on an existing tree, the
        # new polygons are filtered down to the bottom of the tree and become new
        # nodes there. Each set of polygons is partitioned using the first polygon
        # (no heuristic is used to pick a good split).
        def _build(self, polygons):
            if len(polygons) < 1:
                return

            if not self.plane:
                self.plane = polygons[0].plane.clone()

            front = []
            back = []

            for p in polygons:
                self.plane.splitPolygon(p, self.polygons, self.polygons, front, back)

            if len(front) > 0:
                if not self.front:
                    self.front = CSG.Node()
                    self.front.level = self.level + 1
                self.front.build(front)

            if len(back) > 0:
                if not self.back:
                    self.back = CSG.Node()
                    self.back.level = self.level + 1
                self.back.build(back)

        # 上の build だと `RuntimeError: maximum recursion depth exceeded` が起こる
        #
        def build(self, polygons):
            tries = 0
            csgs = [[self, polygons]]
            #print "build: start"
            while csgs:
                tries += 1
                next_csgs = []
                for pair in csgs:
                    csg = pair[0]
                    #sys.stdout.write("csg.build: tries=%d: %d: level=%-10d\r" % (tries, len(csgs), csg.level))
                    #print "build: tries=%d, polygons=%d" % (tries, len(polygons))
                    polygons = pair[1]
                    one_csgs = csg.prepare_build(polygons)
                    if one_csgs:
                        next_csgs += one_csgs
                if len(next_csgs) > 0:
                    csgs = next_csgs
                else:
                    csgs = None
            #sys.stdout.write("\n")

        def prepare_build(self, polygons):
            if len(polygons) < 1:
                return None

            if not self.plane:
                self.plane = polygons[0].plane.clone()

            front = []
            back = []

            for p in polygons:
                self.plane.splitPolygon(p, self.polygons, self.polygons, front, back)
                #print "split: f=%d, b=%d" % (len(front), len(back))

            next_csgs = []
            if len(front) > 0:
                if not self.front:
                    self.front = CSG.Node()
                    self.front.level = self.level + 1
                #print "buid: front: %d" % len(front)
                next_csgs.append([self.front, front])

            if len(back) > 0:
                if not self.back:
                    self.back = CSG.Node()
                    self.back.level = self.level + 1
                #print "buid: back : %d" % len(back)
                next_csgs.append([self.back, back])

            return next_csgs if len(next_csgs) > 0 else None

        def p(self, label=""):
            text = ""
            for i in xrange(self.level):
                text += "  "
            text += "%s: %d" % (label, len(self.polygons))

            if self.front:
                text += self.front.p(label + "f")

            if self.back:
                text += self.back.p(label + "b")

            return text

        def __str__(self):
            text = "%s: level=%d, plane=%s" % (self.name, self.level, self.plane)
            text += "\n  %s" % (self.front)
            text += "\n  %s" % (self.back)
            return text
