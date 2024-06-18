# Copyright (c) Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Lingjie Mei
import bpy
import numpy as np
from numpy.random import uniform

from infinigen.assets.materials import art, fabrics
from infinigen.assets.utils.decorate import distance2boundary, read_normal, remove_faces, subsurf, write_co
from infinigen.assets.utils.draw import remesh_fill
from infinigen.assets.utils.object import new_circle
from infinigen.assets.utils.uv import unwrap_faces, wrap_front_back, wrap_top_bottom
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.util.random import log_uniform
from infinigen.core.util import blender as butil


class PantsFactory(AssetFactory):
    def __init__(self, factory_seed, coarse=False):
        super(PantsFactory, self).__init__(factory_seed, coarse)
        self.width = log_uniform(.45, .55)
        self.size = self.width / 2 + uniform(0, .05)
        self.type = np.random.choice(['underwear', 'shorts', 'pants'])
        match self.type:
            case 'underwear':
                self.length = self.size + uniform(-.02, .02)
            case 'shorts':
                self.length = self.size + uniform(.05, .1)
            case _:
                self.length = self.size + uniform(.5, .7)
        self.neck_shrink = uniform(.1, .15)
        self.thickness = log_uniform(.02, .03)

    def create_asset(self, **params) -> bpy.types.Object:
        x_anchors = 0, self.width / 2, self.width / 2 * (
            1 + self.neck_shrink), self.width / 2 * self.neck_shrink * 2, 0
        y_anchors = 0, 0, -self.length, -self.length, -self.size

        obj = new_circle(vertices=len(x_anchors))
        with butil.ViewportMode(obj, 'EDIT'):
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.edge_face_add()
        write_co(obj, np.stack([x_anchors, y_anchors, np.zeros_like(x_anchors)], -1))
        butil.modify_mesh(obj, 'MIRROR', use_axis=(True, False, False))
        remesh_fill(obj, .02)
        distance2boundary(obj)
        butil.modify_mesh(obj, 'SOLIDIFY', thickness=self.thickness, offset=0)
        x_, y_, z_ = read_normal(obj).T
        remove_faces(obj, (y_ < -.99) | (y_ > .99))
        with butil.ViewportMode(obj, 'EDIT'), butil.Suppress():
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=1e-3)
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_loose()
            bpy.ops.mesh.delete(type='EDGE')
        wrap_top_bottom(obj, self.surface)
        subsurf(obj, 1)
        return obj
