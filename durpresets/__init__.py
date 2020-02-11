# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "DuRPresets",
    "author" : "Nicolas 'Duduf' Dufresne",
    "blender" : (2, 81, 0),
    "version" : (0, 0, 3),
    "location" : "Render buttons (Properties window)",
    "description" : "Exports and imports render presets, collecting the settings from the current scene.",
    "warning" : "",
    "category" : "Render",
    "wiki_url": "http://durpresets-docs.rainboxlab.org"
}

import bpy # pylint: disable=import-error
from bpy_extras.io_utils import ExportHelper # pylint: disable=import-error
from bpy_extras.io_utils import ImportHelper # pylint: disable=import-error
from pathlib import Path
import json

from . import (
    dublf,
)

DUBLF_json = dublf.DUBLF_json

def importViewLayerSettings( viewLayer, preset ):
    for attr in preset["View Layer"]:
        #ignore "use for rendering"
        if attr == "use":
            continue
        if attr == "name":
            continue
        try:
            setattr(viewLayer, attr, preset["View Layer"][attr])
        except:
            pass

class DURPRESETS_OT_exportPreset( bpy.types.Operator, ExportHelper ):
    """Exports the current render settings to a JSON file."""
    bl_idname = "scene.render_export_preset"
    bl_label = "Export Render Preset."
    bl_description = "Export the current render settings as an external preset."
    bl_option = {'REGISTER'}

    # ExportHelper
    filename_ext = ".drprst"
    filter_glob: bpy.props.StringProperty(
            default="*.drprst;*.json;*.txt",
            options={'HIDDEN'},
            )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        view_layer = context.view_layer

        # prepare a serializable object
        renderPreset = {}

        # serialize all
        renderPreset["Render"] = DUBLF_json.serialize( scene.render )
        renderPreset["Cycles"] = DUBLF_json.serialize( scene.cycles )
        renderPreset["Eevee"] = DUBLF_json.serialize( scene.eevee )
        renderPreset["Workbench"] = DUBLF_json.serialize( scene.display.shading )
        renderPreset["Image Settings"] = DUBLF_json.serialize( scene.render.image_settings )
        renderPreset["FFmpeg Settings"] = DUBLF_json.serialize( scene.render.ffmpeg )
        renderPreset["Display Settings"] = DUBLF_json.serialize( scene.display_settings )
        renderPreset["View Settings"] = DUBLF_json.serialize( scene.view_settings )
        renderPreset["View Layer"] = DUBLF_json.serialize( view_layer )
        renderPreset["Playblast"] = DUBLF_json.serialize( scene.playblasyt )

        jsonDump = json.dumps( renderPreset, indent=4 )
        f = Path(self.filepath)
        f.write_text( jsonDump, encoding='utf8' )

        return {'FINISHED'}

class DURPRESETS_OT_importPreset( bpy.types.Operator, ImportHelper ):
    """Imports a render preset (JSON) file."""
    bl_idname = "scene.render_import_preset"
    bl_label = "Import Render Preset."
    bl_description = "Import an external render preset."
    bl_option = {'REGISTER'}

    # ImportHelper
    filename_ext = ".drprst"
    filter_glob = bpy.props.StringProperty(
            default="*.drprst;*.json;*.txt",
            options={'HIDDEN'},
            )

    import_render: bpy.props.BoolProperty( name="General", default=True)
    import_cycles: bpy.props.BoolProperty( name="Cycles", default=True)
    import_eevee: bpy.props.BoolProperty( name="Eevee", default=True)
    import_workbench: bpy.props.BoolProperty( name="Workbench", default=True)
    import_image_settings: bpy.props.BoolProperty( name="Image (output)", default=True)
    import_image_filename: bpy.props.BoolProperty( name="Replace output file name/path", default=False)
    import_ffmpeg: bpy.props.BoolProperty( name="FFmpeg", default=True)
    import_display: bpy.props.BoolProperty( name="Color Management", default=True)
    import_view_layer: bpy.props.BoolProperty( name="View Layer options", default=True)
    import_all_view_layers: bpy.props.BoolProperty( name="Apply to all view layers", default=False)
    import_playblast_settings: bpy.props.BoolProperty( name="Playblast settings", default=False)

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout = self.layout
        layout.label( text="Render settings:")
        layout.prop(self, "import_image_filename")
        layout.prop(self, "import_render")
        layout.prop(self, "import_cycles")
        layout.prop(self, "import_eevee")
        layout.prop(self, "import_workbench")
        layout.separator()
        layout.label( text="Output settings:")
        layout.prop(self, "import_image_settings")
        layout.prop(self, "import_ffmpeg")
        layout.separator()
        layout.label( text="View/Display settings:")
        layout.prop(self, "import_display")
        layout.separator()
        layout.label( text="View Layer settings:")
        layout.prop(self, "import_view_layer")
        layout.prop(self, "import_all_view_layers")
        layout.separator()
        layout.label( text="DuBlast addon:")
        layout.prop(self, "import_playblast_settings")

    def execute(self, context):
        scene = context.scene
        view_layer = context.view_layer

        f = Path(self.filepath)
        jsonDump = f.read_text( encoding='utf8' )
        
        renderPreset = json.loads( jsonDump )

        if self.import_render:
            for attr in renderPreset["Render"]:
                try:
                    if not self.import_image_filename and attr == "filepath":
                        continue
                    setattr(scene.render, attr, renderPreset["Render"][attr])
                except:
                    pass

        if self.import_cycles:
            for attr in renderPreset["Cycles"]:
                try:
                    setattr(scene.cycles, attr, renderPreset["Cycles"][attr])
                except:
                    pass

        if self.import_eevee:
            for attr in renderPreset["Eevee"]:
                try:
                    setattr(scene.eevee, attr, renderPreset["Eevee"][attr])
                except:
                    pass

        if self.import_workbench:
            for attr in renderPreset["Workbench"]:
                try:
                    setattr(scene.display.shading, attr, renderPreset["Workbench"][attr])
                except:
                    pass

        if self.import_image_settings:
            for attr in renderPreset["Image Settings"]:
                try:
                    setattr(scene.render.image_settings, attr, renderPreset["Image Settings"][attr])
                except:
                    pass

        if self.import_ffmpeg:
            for attr in renderPreset["FFmpeg Settings"]:
                try:
                    setattr(scene.render.ffmpeg, attr, renderPreset["FFmpeg Settings"][attr])
                except:
                    pass

        if self.import_display:
            for attr in renderPreset["Display Settings"]:
                try:
                    setattr(scene.display_settings, attr, renderPreset["Display Settings"][attr])
                except:
                    pass

        if self.import_display:
            for attr in renderPreset["View Settings"]:
                try:
                    setattr(scene.view_settings, attr, renderPreset["View Settings"][attr])
                except:
                    pass
        
        if self.import_view_layer:
            importViewLayerSettings( view_layer, renderPreset )

        if self.import_all_view_layers:
            for v_layer in scene.view_layers:
                importViewLayerSettings( v_layer, renderPreset )

        if self.import_playblast_settings and hasattr(scene,'playblast'):
            for attr in renderPreset["Playblast"]:
                try:
                    setattr(scene.playblast, attr, renderPreset["Playblast"][attr])
                except:
                    pass


        return {'FINISHED'}
  
class DURPRESETS_PT_render_presets(bpy.types.Panel):
    bl_label = "Render Presets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("scene.render_export_preset", text="Export")
        row.operator("scene.render_import_preset", text="Import")

classes = (
    DURPRESETS_OT_exportPreset,
    DURPRESETS_OT_importPreset,
    DURPRESETS_PT_render_presets,
)

addon_keymaps = []

def register():
    # register
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # unregister
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
