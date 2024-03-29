import bpy
from bpy.props import (BoolProperty,
                       PointerProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty,
                       )
from bpy.types import (PropertyGroup,
                       Panel)

bl_info = {
    'name': 'WaveModifierHelper',
    'description': 'Adjust the wave modifier',
    'author': 'AIGODLIKE Community:小萌新',
    'version': (0, 0, 1),
    'blender': (3, 0, 0),
    'location': 'tool -> WaveModifierHelper',
    'category': 'AIGODLIKE',
}


class WavePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WaveHelper'

    @classmethod
    def poll(cls, context) -> bool:
        obj = context.object
        mod = obj and obj.modifiers.active
        wave = mod and (mod.type == 'WAVE')
        return wave

    @property
    def is_out(self) -> bool:
        """是向外扩散模式的布尔值

        Returns:
            bool: _description_
        """
        return self.prop.direction == 'out'

    @property
    def prop(self):
        """物体自定义属性

        Returns:
            _type_: _description_
        """
        obj = bpy.context.object
        return obj.wave_modifiers_helper

    @property
    def mod(self) -> 'bpy.types.WaveModifier':
        """活动波修改器

        Returns:
            bpy.types.WaveModifier: _description_
        """
        obj = bpy.context.object
        return obj.modifiers.active


class WaveSet(WavePanel, Panel):
    bl_idname = 'WAVE_SET_MODIFIER_PT_N_Panel'
    bl_label = """WaveHelper"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        mod = self.mod
        prop = self.prop

        col = layout.column()

        row = col.row(align=True, heading='Motion')
        row.prop(mod, 'use_x', expand=True, toggle=1)
        row.prop(mod, 'use_y', expand=True, toggle=1)

        col.prop(mod, 'use_cyclic')

        row = col.row(align=False, heading='Along Normals')
        row.prop(mod, 'use_normal', text='')

        row.prop(mod, 'use_normal_x', expand=True, toggle=1, text='X')
        row.prop(mod, 'use_normal_y', expand=True, toggle=1, text='Y')
        row.prop(mod, 'use_normal_z', expand=True, toggle=1, text='Z')

        col.prop(mod, 'falloff_radius', text='Falloff')
        col.prop(mod, 'height')

        row = col.row(align=True)
        row.prop(prop, 'width')
        row.prop(prop, 'width_use_high_precision',
                 icon='PREFERENCES',
                 icon_only=True)

        col.prop(prop, 'space')

        row = col.row()
        row.prop(prop, 'direction', expand=True)

        col.separator()

        col.prop_search(mod,
                        "vertex_group",
                        context.object,
                        "vertex_groups",
                        text="Vertex Groups")


class WaveAnimation(WavePanel, Panel):
    bl_idname = 'WAVE_SET_ANIMATION_PT_N_Panel'
    bl_label = 'Animation'
    bl_parent_id = WaveSet.bl_idname

    @property
    def stop_frame(self) -> int:
        """停止帧

        Returns:
            int: _description_
        """
        mod = self.mod
        return mod.time_offset + mod.damping_time + mod.lifetime

    @property
    def sum_frame(self) -> int:
        """总帧数，修改器运行时间

        Returns:
            int: _description_
        """
        mod = self.mod
        a = int((mod.lifetime + mod.damping_time) - mod.time_offset)

        if self.is_out:
            return a
        else:
            return self.prop.frame_stop

    @property
    def frame_end(self) -> int:
        """帧结束时间

        Returns:
            int: _description_
        """
        if self.is_out:
            return self.prop.frame_end
        else:
            return self.prop.frame_stop

    @property
    def frame_start(self) -> int:
        """帧开始时间

        Returns:
            int: _description_
        """
        if self.is_out:
            return self.prop.frame_start
        else:
            return self.prop.frame_zero

    def draw_text(self, layout: bpy.types.UILayout):
        """绘制时间帧相关信息

        Args:
            layout (bpy.types.UILayout): _description_
        """
        scene = bpy.context.scene

        if self.prop.cycle:
            layout.label(
                text=f'Total frame count for looping:  {scene.frame_end - scene.frame_start}')
        else:
            layout.label(text=f'Total frame count for motion:{round(self.sum_frame, 2)}')

            layout.label(
                text=f'{"Frame Start" if self.is_out else "Frame Zero"}:{self.frame_start}')
            layout.label(
                text=f'{"Frame End" if self.is_out else "Frame Stop"}:{self.frame_end}')

            layout.label(text=f'Full stop frame:{round(self.stop_frame, 2)}')

    def draw(self, context):
        """主绘制

        Args:
            context (_type_): _description_
        """
        layout = self.layout
        layout.use_property_split = True
        mod = self.mod
        prop = self.prop

        row = layout.row(align=True)

        row.prop(prop, 'frequency',
                 )
        row.prop(prop, 'cycle',
                 icon='FILE_REFRESH',
                 icon_only=True
                 )
        if prop.cycle:
            layout.prop(prop, 'offset',
                        )
            layout.separator()
            col = layout
        else:
            layout.separator()
            col = layout.column(align=True)
            if self.is_out:
                col.prop(prop, 'frame_start')
                col.prop(prop, 'frame_end')
            else:
                col.prop(prop, 'frame_zero')
                col.prop(prop, 'frame_stop')
            col.prop(mod, 'damping_time', text='Damping')
            col.separator()

        self.draw_text(col)


class ModifierProper(PropertyGroup):

    @property
    def sum_frame(self) -> int:
        mod = self.mod
        a = int(mod.lifetime + mod.damping_time)

        if self.is_out:
            return a
        else:
            return self.frame_stop

    @property
    def mod(self) -> bpy.types.WaveModifier:
        obj = bpy.context.object
        if not obj:
            return
        mod = obj.modifiers.active
        return mod

    @property
    def is_out(self):
        return self.direction == 'out'

    @property
    def factor(self) -> float:
        if self.width_use_high_precision:
            import math
            return math.e
        return 2

    def set_wave(self, context: 'bpy.context'):
        """
        TODO 设置时间帧内波次数

        # 启动

        宽度
        窄度值大于 2/宽

        """

        mod = self.mod
        mod.narrowness = (self.factor * 2) / self.width
        mod.width = (self.space + self.width) / 2

        self.set_speed(context)

    @property
    def start_frame(self):
        """获取开始帧

        Returns:
            _type_: _description_
        """
        if self.is_out:
            return self.frame_start
        else:
            return 0

    @property
    def end_frame(self):
        """获取结束帧

        Returns:
            _type_: _description_
        """
        if self.is_out:
            return self.frame_end
        else:
            return bpy.context.scene.frame_end

    def set_speed(self, context: 'bpy.context'):
        """设置速度

        Args:
            context (bpy.context): _description_
        """
        mod = self.mod

        if self.is_out:
            mod.time_offset = self.frame_start + int(self.mod.width)
            mod.lifetime = self.frame_end - mod.time_offset
        else:
            mod.time_offset = self.frame_stop
            mod.lifetime = (self.frame_zero - self.frame_stop)
            mod.damping_time = self.frame_stop - self.frame_zero

        scene = context.scene

        speed = ((mod.width * 2.0) /
                 ((scene.frame_end - scene.frame_start) + 1.0))
        mod.speed = speed * self.frequency

        if not self.is_out:
            mod.speed *= -1

    def update_cycle(self, context):
        """设置循环

        Args:
            context (_type_): _description_
        """
        if self.cycle:
            frame = context.scene.frame_end - context.scene.frame_start
            value = (114 if not self.is_out else -514)
            self.mod.time_offset = frame * value
            self.mod.lifetime = self.mod.damping_time = 0

            self.mod.time_offset += self.offset

    def set_modifier_prop(self, context):
        """设置修改器属性
        如果活动修改器是波则修改值"""
        obj = bpy.context.active_object
        mod = (obj and obj.modifiers.active)
        typ = (mod and (mod.type == 'WAVE'))
        if typ:
            self.set_wave(context)
            self.update_cycle(context)

    offset: IntProperty(name='Offset',
                        default=0,
                        update=set_modifier_prop,
                        )

    cycle: BoolProperty(name='Set loop animation',
                        update=set_modifier_prop,
                        )

    width: FloatProperty(name='Width',
                         description='Width of each wave',
                         update=set_modifier_prop,
                         default=1,
                         min=0.01
                         )

    width_use_high_precision: BoolProperty(name='High precision',
                                           update=set_modifier_prop,
                                           default=False,
                                           )

    space: FloatProperty(name='Wave spacing',
                         description='The spacing between each wave',
                         update=set_modifier_prop,
                         min=0,
                         )
    frequency: IntProperty(name='Frequency',
                           description='In one second, the number of oscillations of particles, directly expressed as the reciprocal of the period',
                           update=set_modifier_prop,
                           default=10,
                           min=1,
                           )

    direction: EnumProperty(name='Direction',
                            items=[('out', 'Diffusion', ''),
                                   ('in', 'Shrink', ''),
                                   ],
                            update=set_modifier_prop,
                            )

    frame_end: IntProperty(name='Frame End',
                           update=set_modifier_prop,
                           default=100)
    frame_start: IntProperty(name='Frame Start',
                             update=set_modifier_prop,
                             default=0)

    def get_zero(self):
        if 'zero' in self:
            return self['zero']
        return 5

    def set_zero(self, value):
        self['zero'] = value
        if value >= self.frame_stop:
            self.frame_stop = self.frame_zero + 1

    frame_zero: IntProperty(name='Frame Zero',
                            update=set_modifier_prop,
                            get=get_zero,
                            set=set_zero,
                            default=10,
                            )

    def get_stop(self):
        if 'stop' in self:
            return self['stop']
        return 10

    def set_stop(self, value):
        self['stop'] = value
        print(self.frame_zero, value)
        if self.frame_zero >= value:
            self.frame_zero = value - 1

    frame_stop: IntProperty(name='Frame Stop',
                            update=set_modifier_prop,
                            get=get_stop,
                            set=set_stop,
                            )

class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except(ValueError):
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)


# Set
############
from . import zh_CN

WaveModifierHelper_zh_CN = TranslationHelper('WaveModifierHelper_zh_CN', zh_CN.data)
WaveModifierHelper_zh_HANS = TranslationHelper('WaveModifierHelper_zh_HANS', zh_CN.data, lang='zh_HANS')


class_tuple = (WaveSet,
               WaveAnimation,
               ModifierProper,
               )
register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuple)


def register():
    register_class()
    bpy.types.Object.wave_modifiers_helper = PointerProperty(
        type=ModifierProper)
    if bpy.app.version < (4, 0, 0):
        WaveModifierHelper_zh_CN.register()
    else:
        WaveModifierHelper_zh_CN.register()
        WaveModifierHelper_zh_HANS.register()

def unregister():
    unregister_class()
    del bpy.types.Object.wave_modifiers_helper
    if bpy.app.version < (4, 0, 0):
        WaveModifierHelper_zh_CN.unregister()
    else:
        WaveModifierHelper_zh_CN.unregister()
        WaveModifierHelper_zh_HANS.unregister()