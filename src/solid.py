# coding:utf-8
# 頂点と面をまとめたもの

class Solid:

    # 面
    class Face:
        # indices は反時計回りが表 (CSG.js とは逆)

        def __init__(self, indices, color=None):
            i_first = indices[0]
            i_last = indices[len(indices) - 1]
            if not i_first == i_last:
                if not type(indices) == "list":
                    indices = list(indices)
                indices.append(i_first)
            self.indices = indices
            self.color = color

        def clone(self):
            return Solid.Face(self.indices[:], self.color[:] if self.color else None)

    def __init__(self):
        # これの引数に vertices=[] を入れていたら、前に作った vertices がなぜかコピーされる
        self.vertices = []
        self.faces = []

    def is_empty(self):
        return len(self.faces) < 1

    def clear(self):
        self.vertices = []
        self.faces = []

    def detach_to(self, rhs):
        rhs.vertices = self.vertices
        rhs.faces = self.faces
        self.clear()

    def clone(self):
        rhs = Solid()
        rhs.vertices = map(lambda v:v[:], self.vertices)
        rhs.faces = map(lambda f:f.clone(), self.faces)
        return rhs

    def __str__(self):
        text = "%d vertices, %d faces ...\n" % (len(self.vertices), len(self.faces))
        for f in self.faces:
            i_text = None
            v_text = None
            for i in f.indices[:-1]:
                if i_text:
                    i_text += ","
                    v_text += ","
                else:
                    i_text = "("
                    v_text = "("
                i_text += "%d" % i

                v = self.vertices[i]
                v_text += " ["
                for d in xrange(3):
                    v_text += " %f" % v[d]
                v_text += " ]"

            text += i_text + ") = " + v_text + ")"
            if f.color:
                text += " .. color(%s)" % f.color
            text += "\n"
        return text

    def append_solid(self, rhs):
        for f in rhs.faces:
            indices = []
            for i0 in f.indices[:-1]:
                v0 = rhs.vertices[i0]
                i1 = self.append_vertex(v0[:])
                indices.append(i1)
            self.append_plane(indices, f.color)

    def append_vertices(self, vertices):
        self.vertices += vertices

    # @param utm coord.UTM
    def append_utm(self, utm):
        return self.append_vertex([utm.x, utm.y, utm.z])

    # @param vertex [3]
    def append_vertex(self, vertex):
        index = len(self.vertices)
        self.vertices.append(vertex)
        return index

    def round_value(self, vertex, decimals=None):
        if decimals >= 0:
            array = []
            multiply = 1
            for i in xrange(decimals):
                multiply *= 10
            for v in vertex:
                array.append(int(v * multiply))
            return array
        else:
            return vertex

    def find_vertex(self, vertex, decimals=None):
        index = 0
        vertex = self.round_value(vertex, decimals)
        #print "find: decimals=%d: %s" % (decimals, vertex)
        for v in self.vertices:
            v = self.round_value(v, decimals)
            if v[0] == vertex[0] and v[1] == vertex[1] and v[2] == vertex[2]:
                #print "  found: %s" % v
                return index
            #print "  v: %s" % v
            index += 1
        return None
    
    def create_polygon(self, vertices, color=None, as_tri=True, reversed=False):
        if len(vertices) < 3:
            return

        indices = []
        for v in vertices:
            i = self.append_vertex(v)
            indices.append(i)

        self.append_polygon(indices, color=color, as_tri=as_tri, reversed=reversed)

    def append_polygon(self, indices, color=None, as_tri=True, reversed=False):
        if len(indices) < 3:
            return

        if as_tri:
            i0 = indices[0]
            for i in xrange(2,len(indices)):
                i1 = indices[i-1]
                i2 = indices[i]
                self.append_tri(i0, i1, i2, color=color, reversed=reversed)
        else:
            self.append_plane(indices, color=color, reversed=reversed)

    def create_square(self, v0, v1, v2, v3, color=None, as_tri=True, reversed=False):
        i0 = self.append_vertex(v0)
        i1 = self.append_vertex(v1)
        i2 = self.append_vertex(v2)
        i3 = self.append_vertex(v3)
        self.append_square(i0, i1, i2, i3, color=color, as_tri=as_tri, reversed=reversed)

    def create_tri(self, v0, v1, v2, color=None, reversed=False):
        i0 = self.append_vertex(v0)
        i1 = self.append_vertex(v1)
        i2 = self.append_vertex(v2)
        self.append_tri(i0, i1, i2, color=color, reversed=reversed)

    def append_square(self, i0, i1, i2, i3, color=None, as_tri=True, reversed=False):
        if reversed:
            tmp = i0
            i0 = i3
            i3 = tmp
            tmp = i2
            i2 = i1
            i1 = tmp

        if as_tri:
            self.faces.append(Solid.Face([i0, i1, i2], color))
            self.faces.append(Solid.Face([i0, i2, i3], color))
        else:
            self.faces.append(Solid.Face([i0, i1, i2, i3], color))

    def append_tri(self, i0, i1, i2, color=None, reversed=False):
        if reversed:
            self.faces.append(Solid.Face([i2, i1, i0], color))
        else:
            self.faces.append(Solid.Face([i0, i1, i2], color))

    def append_plane(self, indices, color=None, reversed=False):
        if reversed:
            indices.reverse()
        self.faces.append(Solid.Face(indices, color))

    def append_face(self, face):
        self.faces.append(face)

