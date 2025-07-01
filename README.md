# Convert Rotation Mode

[![GitHub license](https://img.shields.io/github/license/L0Lock/convertRotationMode?style=for-the-badge&labelColor=rgb(64,64,64))](https://github.com/L0Lock/convertRotationMode/blob/master/LICENSE) ![Minimum Supported Blender Version](https://img.shields.io/badge/Blender-4.2LTS+-green?style=for-the-badge&logo=blender&logoColor=white&labelColor=rgb(64,64,64)) [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H818FHX)

-----

*Convert Rotation Mode* (*CRM*) is an addon for Blender that allows you to change the rotation mode of the selected bones and preserve the animation or poses you already made.

![feature image](Prez/Feature.png)

## Installation

> [!CAUTION]
> **Requires [Copy Global Transform addon](https://wiki.blender.org/wiki/Reference/Release_Notes/3.1/Add-ons#Copy_Global_Transform), shipped with Blender since v3.1.0. and up**
> There's a handy button in the addon's preference to enable it if needed.

### Simple method:

- Go to Edit > Preferences > Get Extensions
- Search "Convert Rotation Mode"
- Hit the Install button

### Not so simple method:

- Download the [**latest release**](https://github.com/L0Lock/convertRotationMode/releases/latest).

- Go to Edit > Preferences > Get Extensions

- Hit the 🔽 button > Install from Disk

- Browse the zip file you downloaded.

![demo enable dependency](./Prez/demo_enable_dependency.gif)

## Usage:

![demo basic function](./Prez/demo_basic_function.gif)

Select one or more bones in Pose mode, select the rotation mode you want them to use, hit the <kbd>Convert!</kbd> button.

It will automatically scan through all the keyframes of the selected bones in the timeline.

![Addons Preferences](./Prez/addon_preferences.gif)

To customize the sidebar tab in which the addon appears, go to the addon's preferences.

![Rmodes cheat sheet](./Prez/Rmodes_cheat_sheet.gif)

If you are unsure what rotation mode to use, look at the rotation modes cheat sheet!

Please not these are merely suggestions, what you will actually need may vary from one rig to another or even from one animation to another.

Note that there are two main coordinates system for bones. Blender uses Y down, so this is most likely the one you will use. But you might need to look at the X down in some cases like exporting to softwares that can only ready X down.

## Recommanded Rotation Modes:

| Bone/Body Part    | Rotation Mode |
| ----------------- | ------------- |
| COG               | zxy           |
| Hip               | zxy           |
| Leg Joints        | yzx           |
| Shoulder/Clavicle | yxz           |
| Upper Arm         | zyx (or yzx)  |
| Lower Arm         | zyx (or yzx)  |
| Wrist             | yzx           |
| Spine Base        | zxy           |
| Mid Spine         | yzx           |
| Chest             | zxy           |
| Neck              | yxz           |
| Head              | yxz           |

## Contributing

I recently started using [PyType](https://github.com/google/pytype) type-checker. While I'm not sure it's a big deal whether you use it, or another one, or none at all, it definitely helps avoid issues if we all use the same. Hence furnished the repowith its own [requirements.txt](https://github.com/L0Lock/convertRotationMode/blob/main/requirements.txt). 

To use it, create a virtual environment in your local repo ([see guide here, its a tad different for each operating system](https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/), then once created and activated, install the required packages using:

```bash
pip install -r requirements.txt
```

This way we are sure to be on the same base :] 
