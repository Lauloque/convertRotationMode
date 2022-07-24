# Convert Rotation Mode

[![GitHub license](https://img.shields.io/github/license/L0Lock/convertRotationMode?style=for-the-badge)](https://github.com/L0Lock/convertRotationMode/blob/master/LICENSE) ![Latest Supported Blender Version](https://img.shields.io/badge/Blender-v3.2.0-orange?style=for-the-badge&logo=blendere)

-----

[![ko-fi](Prez/SupportOnKofi.jpg)](https://ko-fi.com/l0lock) [![uTip](Prez/SupportOnUtip.jpg)](https://www.utip.io/l0lock) [![ArtStation](Prez/BuyOnArtstation.jpg)](https://artstn.co/m/276y) [![Gumroad](Prez/BuyOnGumroad.jpg)](https://gum.co/gizmotools)

Blender addon to change the rotation mode of a bone while preserving the current poses.

**Requires [Copy Global Transform addon](https://wiki.blender.org/wiki/Reference/Release_Notes/3.1/Add-ons#Copy_Global_Transform), shipped with Blender since v3.1.0.**

**⚠️ Work in progress, use at your own risk! ⚠️**

## Recommanded Rotation Modes:

These are merely suggestions, may vary from one rig to another or even from one animation to another.

Note that there are two main coordinates system for bones. Blender uses Y down, as well as Maya, and 3DS uses X down.

### For Y down coordinates (Blender):

- COG: zxy
- Hip:  zxy
- leg joints:  yzx
- shoulder/clav: yxz
- upper arm: zyx (or yzx)
- lower arm: zyx (or yzx)
- wrist: yzx
- spine base: zxy
- mid spine: yzx
- chest: zxy
- neck: yxz
- head: yxz

### For X down coordinates

- COG: zxy
- Hip: zxy
- leg joints: xzy
- shoulder/clav: xyz
- upper arm: zxy
- lower arm: zxy
- wrist: xyz (or yzx?)
- fingers: yzx
- spine base: zxy
- mid spine: xzy
- chest: zxy
- neck: yxz
- head: yxz
