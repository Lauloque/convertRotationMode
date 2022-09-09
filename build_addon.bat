:: Target folder where to copy the addon's content.
:: I use a custom directory to avoid having to reinstall addons at each new Blender version
:: If you want to do the same, don't forget to add that path to Blender > Edit menu > Preferences > File Paths tab > Scripts

set targetFolder="C:\AppInstall\Blender\MyScripts\addons\"

:: Input files and folders. See examples after ::
:: Folders will be copied with their full content.
:: Put them between quotation marks, one per line, and increment the number between [ ]
:: You can write in absolute and relative paths, I chose relative for simplicity.

set inputFiles[0]="convert_Rotation_Mode.py"
:: set inputFiles[1]="example_file.ext"
:: set inputFiles[2="example folder"

(for %%a in (%inputFiles%) do ( 
   xcopy /y /e %%a %targetFolder%
))

EOF