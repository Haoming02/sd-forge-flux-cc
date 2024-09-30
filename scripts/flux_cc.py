from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules.ui_components import InputAccordion
from modules import shared, scripts

from lib_fluxcc.const import CHANNELS, Param, Slider
from lib_fluxcc.callback import hook_callbacks
from lib_fluxcc.style import StyleManager
from lib_fluxcc.xyz import xyz_support

from random import seed
import gradio as gr
import os


WHEEL = os.path.join(scripts.basedir(), "scripts", "vectorscope.png")
VERSION = "1.0.0"


style_manager = StyleManager()
style_manager.load_styles()
hook_callbacks()


class FluxCC(scripts.Script):

    def __init__(self):
        self.xyzCache = {}
        xyz_support(self.title(), self.xyzCache)

    def title(self):
        return "Flux CC"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        mode: str = "img" if is_img2img else "txt"

        with InputAccordion(
            value=False, label=f"{self.title()} v{VERSION}", elem_id=f"flux-cc-{mode}"
        ) as enable:

            with gr.Row():
                bri = Slider("Brightness")
                con = Slider("Contrast")
            temp = Slider("Temperature", ("Cold", "Warm"))

            with gr.Row():

                colors = []
                with gr.Column():
                    for i in range(len(CHANNELS)):
                        colors.append(Slider(f"Param {i + 1}", CHANNELS[i]))

                whl = gr.Image(
                    value=WHEEL,
                    interactive=False,
                    container=False,
                    elem_id=f"flux-colorwheel-{mode}",
                )

                whl.do_not_save_to_config = True

            with gr.Accordion("Styles", open=False):

                with gr.Row(elem_classes="style-rows"):
                    style_choice = gr.Dropdown(
                        label="Flux Styles", choices=style_manager.list_style(), scale=3
                    )
                    apply_btn = gr.Button(
                        value="Apply Style", elem_id=f"flux-apply-{mode}", scale=2
                    )
                    refresh_btn = gr.Button(value="Refresh Style", scale=2)

                with gr.Row(elem_classes="style-rows"):
                    style_name = gr.Textbox(
                        label="Style Name", lines=1, max_lines=1, scale=3
                    )
                    save_btn = gr.Button(
                        value="Save Style", elem_id=f"flux-save-{mode}", scale=2
                    )
                    delete_btn = gr.Button(value="Delete Style", scale=2)

                if getattr(shared.opts, "fc_no_defaults", True):
                    style_choice.do_not_save_to_config = True

                [
                    setattr(comp, "do_not_save_to_config", True)
                    for comp in (
                        apply_btn,
                        refresh_btn,
                        style_name,
                        save_btn,
                        delete_btn,
                    )
                ]

            with gr.Accordion("Advanced Settings", open=False):
                with gr.Row():
                    doAD = gr.Checkbox(label="Process Adetailer")
                    doRN = gr.Checkbox(label="Randomize using Seed")

                scaling = gr.Radio(
                    choices=("Flat", "Cos", "Sin", "1 - Cos", "1 - Sin"),
                    label="Scaling Settings",
                    value="Cos",
                )

            comps: tuple[gr.components.Component] = (
                bri,
                con,
                temp,
                *colors,
                doAD,
                doRN,
                scaling,
            )

            apply_btn.click(
                fn=style_manager.get_style,
                inputs=[style_choice],
                outputs=[*comps],
            )

            save_btn.click(
                fn=lambda *args: gr.update(choices=style_manager.save_style(*args)),
                inputs=[style_name, *comps],
                outputs=[style_choice],
            )

            delete_btn.click(
                fn=lambda name: gr.update(choices=style_manager.delete_style(name)),
                inputs=[style_name],
                outputs=[style_choice],
            )

            refresh_btn.click(
                fn=lambda: gr.update(choices=style_manager.load_styles()),
                outputs=[style_choice],
            )

            with gr.Row():
                reset_btn = gr.Button(value="Reset")
                random_btn = gr.Button(value="Randomize")

                def on_reset():
                    return [
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=Param.default),
                        gr.update(value=False),
                        gr.update(value=False),
                        gr.update(value="Cos"),
                    ]

                def on_random():
                    return [
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                        gr.update(value=Param.rand()),
                    ]

                reset_btn.click(
                    fn=on_reset,
                    outputs=[*comps],
                    show_progress="hidden",
                    queue=False,
                )

                random_btn.click(
                    fn=on_random,
                    outputs=[bri, con, temp, *colors],
                    show_progress="hidden",
                    queue=False,
                )

        self.paste_field_names = []
        self.infotext_fields = [
            (enable, "Flux CC Enabled"),
            (bri, "Flux CC Brightness"),
            (con, "Flux CC Contrast"),
            (temp, "Flux CC Temperature"),
            (doAD, "Flux CC Proc Ade"),
            (doRN, "Flux CC Seed Randomize"),
            (scaling, "Flux CC Scaling"),
        ]

        for i in range(len(CHANNELS)):
            self.infotext_fields.append((colors[i], f"Flux CC Param {i + 1}"))

        for comp, name in self.infotext_fields:
            if getattr(shared.opts, "fc_no_defaults", True):
                comp.do_not_save_to_config = True
            self.paste_field_names.append(name)

        return [enable, *comps]

    def process_batch(
        self,
        p,
        enable: bool,
        bri: float,
        con: float,
        temp: float,
        param1: float,
        param2: float,
        param3: float,
        param4: float,
        param5: float,
        doAD: bool,
        doRN: bool,
        scaling: str,
        batch_number: int,
        prompts: list[str],
        seeds: list[int],
        subseeds: list[int],
    ):

        enable = self.xyzCache.pop("Enable", str(enable)).lower().strip() == "true"

        if not enable:
            if len(self.xyzCache) > 0:
                print("\n[Flux.CC] x [X/Y/Z Plot] Extension is not Enabled!\n")
                self.xyzCache.clear()

            setattr(KDiffusionSampler, "flux_cc", {"enable": False})
            return p

        if "Random" in self.xyzCache.keys():
            print("[Flux.CC] x [X/Y/Z Plot] Randomize is Enabled")
            if len(self.xyzCache) > 1:
                print("Some parameters will be overridden!")

            cc_seed = int(self.xyzCache.pop("Random"))
        else:
            cc_seed = int(seeds[0]) if doRN else None

        scaling = str(self.xyzCache.pop("Scaling", scaling))

        if cc_seed:
            seed(cc_seed)

            bri = Param.rand()
            con = Param.rand()
            temp = Param.rand()

            param1 = Param.rand()
            param2 = Param.rand()
            param3 = Param.rand()
            param4 = Param.rand()
            param5 = Param.rand()

        else:
            bri = float(self.xyzCache.pop("Brightness", bri))
            con = float(self.xyzCache.pop("Contrast", con))
            temp = float(self.xyzCache.pop("Temperature", temp))

            param1 = float(self.xyzCache.pop("Param1", param1))
            param2 = float(self.xyzCache.pop("Param2", param2))
            param3 = float(self.xyzCache.pop("Param3", param3))
            param4 = float(self.xyzCache.pop("Param4", param4))
            param5 = float(self.xyzCache.pop("Param5", param5))

        p.extra_generation_params.update(
            {
                "Flux CC Enabled": enable,
                "Flux CC Brightness": bri,
                "Flux CC Contrast": con,
                "Flux CC Temperature": temp,
                "Flux CC Param 1": param1,
                "Flux CC Param 2": param2,
                "Flux CC Param 3": param3,
                "Flux CC Param 4": param4,
                "Flux CC Param 5": param5,
                "Flux CC Proc Ade": doAD,
                "Flux CC Seed Randomize": doRN,
                "Flux CC Scaling": scaling,
                "Flux CC Version": VERSION,
            }
        )

        steps: int = getattr(p, "firstpass_steps", None) or p.steps

        bri, con, temp, param1, param2, param3, param4, param5 = [
            v / steps / 10.0
            for v in (bri, con, temp, param1, param2, param3, param4, param5)
        ]

        setattr(
            KDiffusionSampler,
            "flux_cc",
            {
                "enable": True,
                "bri": bri,
                "con": con,
                "temp": temp,
                "param1": param1,
                "param2": param2,
                "param3": param3,
                "param4": param4,
                "param5": param5,
                "doAD": doAD,
                "scaling": scaling,
                "step": steps,
            },
        )

        return p
