#!/usr/bin/env python
# coding: utf-8
#
# PLY:
#   http://paulbourke.net/dataformats/ply/
#   http://www.cs.gunma-u.ac.jp/~nagai/wiki/index.php?ply%20%A5%D5%A5%A1%A5%A4%A5%EB%20%A5%D5%A5%A9%A1%BC%A5%DE%A5%C3%A5%C8
#

import re
from solid import Solid
from text_reader import TextReader

def read(filename):
    io = TextReader(filename)
    if not io.readline() == "ply":
        assert False, "file does not start ply: filename=%s" % filename
    if not io.readline() == "format ascii 1.0":
        assert False, "file is not ascii: filename=%s" % filename

    vertex_count = 0
    face_count = 0
    has_color = False

    while True:
        line = io.readline()
        if line == "end_header":
            break

        if line == "property uchar red":
            has_color = True

        match = re.match(r"element vertex (\d+)", line)
        if match:
            vertex_count = int(match.group(1))
            continue

        match = re.match(r"element face (\d+)", line)
        if match:
            face_count = int(match.group(1))
            continue

    if vertex_count == 0:
        assert False, "no vertex"

    solid = Solid()
    for i in xrange(vertex_count):
        line = io.readline()
        items = line.split(" ")
        solid.append_vertex([float(items[0]), float(items[1]), float(items[2])])

    for i in xrange(face_count):
        line = io.readline()
        items = line.split(" ")
        count = int(items[0]) - 1
        indices = []
        color = None
        for v in xrange(count):
            indices.append(int(items[v + 1]))

        if has_color:
            color = []
            for c in xrange(count, count + 3):
                color.append(int(items[c + 2]))

        solid.append_plane(indices, color)

    io.close()
    return solid
