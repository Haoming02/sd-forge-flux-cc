from modules import scripts


def _grid_reference():
    for data in scripts.scripts_data:
        if data.script_class.__module__ in (
            "scripts.xyz_grid",
            "xyz_grid.py",
        ) and hasattr(data, "module"):
            return data.module

    raise SystemError("Could not find X/Y/Z Plot...")


def xyz_support(ext: str, cache: dict):

    def _apply(field):
        def _(p, x, xs):
            cache.update({field: x})

        return _

    def _bool():
        return ("False", "True")

    def _scaling():
        return ("Flat", "Cos", "Sin", "1 - Cos", "1 - Sin")

    xyz_grid = _grid_reference()

    extra_axis_options = [
        xyz_grid.AxisOption(f"[{ext}] Enable", str, _apply("Enable"), choices=_bool),
        xyz_grid.AxisOption(f"[{ext}] Brightness", float, _apply("Brightness")),
        xyz_grid.AxisOption(f"[{ext}] Contrast", float, _apply("Contrast")),
        xyz_grid.AxisOption(f"[{ext}] Temperature", float, _apply("Temperature")),
        xyz_grid.AxisOption(f"[{ext}] Param 1", float, _apply("Param1")),
        xyz_grid.AxisOption(f"[{ext}] Param 2", float, _apply("Param2")),
        xyz_grid.AxisOption(f"[{ext}] Param 3", float, _apply("Param3")),
        xyz_grid.AxisOption(f"[{ext}] Param 4", float, _apply("Param4")),
        xyz_grid.AxisOption(f"[{ext}] Param 5", float, _apply("Param5")),
        xyz_grid.AxisOption(f"[{ext}] Scaling", str, _apply("Scale"), choices=_scaling),
        xyz_grid.AxisOption(f"[{ext}] Randomize", int, _apply("Random")),
    ]

    xyz_grid.axis_options.extend(extra_axis_options)
