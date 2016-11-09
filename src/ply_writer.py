#!/usr/bin/env python
# coding: utf-8
#
# PLY:
#   http://paulbourke.net/dataformats/ply/
#   http://www.cs.gunma-u.ac.jp/~nagai/wiki/index.php?ply%20%A5%D5%A5%A1%A5%A4%A5%EB%20%A5%D5%A5%A9%A1%BC%A5%DE%A5%C3%A5%C8
#

class PLYWriter:

    def __init__(self, filename):
        self.io = open(filename, "w")
        self.vertex_color = None
        self.face_color = None

    def close(self):
        self.io.close

    def _write_header_color(self):
        self.io.write("""property uchar red
property uchar green
property uchar blue
""")

    def _append_color(self, line, color):
        if not color == None:
            return line + " %d %d %d" % (color[0], color[1], color[2])
        else:
            return line

    def write_header(self, vertex_count, face_count = 0):
        self.io.write("""ply
format ascii 1.0
comment made by washi
element vertex %d
property double x
property double y
property double z
""" % (vertex_count))

        if self.vertex_color:
            self._write_header_color()

        if face_count > 0:
            self.io.write("""element face %d
property list uchar int vertex_index
""" % (face_count))
        
            if self.face_color:
                self._write_header_color()

        self.io.write("end_header\n")

    def write_solid(self, solid):
        vertex_count = len(solid.vertices)
        face_count = len(solid.faces)
        self.write_header(vertex_count, face_count)
       
        for v in solid.vertices:
            line = "%f %f %f" % (v[0], v[1], v[2])
            line = self._append_color(line, self.vertex_color)
            self.io.write(line + "\n")
       
        for face in solid.faces:
            line = "%d" % len(face.indices)
            for v in face.indices:
                line += " %d" % v
            line = self._append_color(line, self.face_color if face.color == None else face.color)
            self.io.write(line + "\n")

