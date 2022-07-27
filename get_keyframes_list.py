import bpy
from bpy.types import (Context, Operator, )

def Key_Frame_Points(): #Gets the key-frame values as an array.
    KEYFRAME_POINTS_ARRAY = []
    fcurves = bpy.context.active_object.animation_data.action.fcurves

    for curve in fcurves:
        keyframePoints = curve.keyframe_points
        for keyframe in keyframePoints:
#            print('TOTAL FRAMES ARE: {}'.format(keyframe.co[0]))
            KEYFRAME_POINTS_ARRAY.append(keyframe.co[0])
            KEYFRAME_POINTS_ARRAY = list(dict.fromkeys(KEYFRAME_POINTS_ARRAY))
    return KEYFRAME_POINTS_ARRAY

print(Key_Frame_Points())