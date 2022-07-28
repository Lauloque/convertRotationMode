import bpy, re

dev_mode = True
C = bpy.context

def get_fcs(obj):
    try:    return obj.animation_data.action.fcurves
    except: return None

def get_keyed_frames():
    fcs = get_fcs(bpy.context.object)

    if fcs is None:
        print("No animation_data / invalid object")
        return None

    ARRAY = []
    d = "\"]"
    
    for fc in fcs:
        bone_name = fc.data_path
        index = fc.array_index

        ### EXTRACT BONES PATHS FROM FCURVES
        if bone_name[: 10] != "pose.bones": continue
        ### EXTRACT BONE NAMES FROM BONES PATHS
        try:
            bone_name = re.search('pose.bones\["(.+?)\"].', bone_name).group(1)
        except AttributeError:
            bone_name = "search failed!"
        ### BUILD 
        ARRAY.append({
            "bone_name": bone_name,
            "keyed_frames": [kp.co[0] for kp in fc.keyframe_points]
        })
        
        #### CLEANUP DUPLICATES
        keyed_frames_list = [] 
        for i in ARRAY: 
            if i not in keyed_frames_list: 
                keyed_frames_list.append(i) 
        
    if ARRAY is None and dev_mode == True:
        print("Failed to get list of Bones")

    return keyed_frames_list

keyed_frames_list = get_keyed_frames()
#if dev_mode == True:
#    for A in keyed_frames_list:
#        print(f'Bone {A["bone_name"]} has keys in frames {A["keyed_frames"]}')

for A in keyed_frames_list:
    print("A = ", A["bone_name"])
    print("active bone is ", C.active_bone.name, "\n \n")
    if A["bone_name"] == C.active_bone.name:
        print("########  Using keyed_frames_list of",A["bone_name"],"  ########")
        for B in A["keyed_frames"]:
            C.active_bone.keyframe_insert(data_path="hide", frame=int(B))
            C.scene.frame_current = int(B)
            print('jumped to frame ', int(B))
        break
        
        