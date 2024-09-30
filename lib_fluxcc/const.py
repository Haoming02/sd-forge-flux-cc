import gradio as gr
import random

CHANNELS = (
    ("Yellow", "Blue"),
    ("Brown", "Cyan"),
    ("Red", "Green"),
    ("Pink", "Lime"),
    ("Purple", "Olive"),
)


class Param:

    minimum: float = -5.0
    maximum: float = 5.0
    default: float = 0.0

    @classmethod
    def rand(cls) -> float:
        return round(random.uniform(cls.minimum, cls.maximum), 2)


def Slider(label: str, info: tuple[str] = None) -> gr.Slider:
    return gr.Slider(
        label=label,
        info=" | ".join(info) if info else None,
        value=Param.default,
        minimum=Param.minimum,
        maximum=Param.maximum,
        step=0.05,
    )
