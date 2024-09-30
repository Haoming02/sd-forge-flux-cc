from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules.script_callbacks import on_script_unloaded, on_ui_settings
from functools import wraps
import torch

from .scaling import apply_scaling
from .settings import settings


original_callback = KDiffusionSampler.callback_state


@torch.no_grad()
@torch.inference_mode()
@wraps(original_callback)
def cc_callback(self, d):

    if not self.flux_cc["enable"]:
        return original_callback(self, d)

    if getattr(self.p, "_ad_inner", False) and not self.flux_cc["doAD"]:
        return original_callback(self, d)

    assert not self.p.sd_model.is_webui_legacy_model()

    source: torch.Tensor = d["x"]
    target: torch.Tensor = torch.ones_like(d["x"])
    batchSize = int(d["x"].size(0))

    bri, con, temp, param1, param2, param3, param4, param5 = apply_scaling(
        self.flux_cc["scaling"],
        d["i"],
        self.flux_cc["step"],
        self.flux_cc["bri"],
        self.flux_cc["con"],
        self.flux_cc["temp"],
        self.flux_cc["param1"],
        self.flux_cc["param2"],
        self.flux_cc["param3"],
        self.flux_cc["param4"],
        self.flux_cc["param5"],
    )

    for i in range(batchSize):

        source[i][0] -= target[i][0] * temp

        source[i][1] += target[i][1] * bri
        source[i][12] += target[i][12] * bri

        source[i][8] += target[i][8] * param1
        source[i][9] -= target[i][9] * param1

        source[i][6] += target[i][6] * param2
        source[i][7] -= target[i][7] * param2

        source[i][2] -= target[i][2] * param3
        source[i][10] += target[i][10] * param3

        source[i][5] += target[i][5] * param4
        source[i][11] -= target[i][11] * param4

        source[i][3] -= target[i][3] * param5
        source[i][4] += target[i][4] * param5

        source[i][13] += target[i][13] * con
        source[i][14] += target[i][14] * con
        source[i][15] += target[i][15] * con

    return original_callback(self, d)


def restore_callback():
    KDiffusionSampler.callback_state = original_callback


def hook_callbacks():
    KDiffusionSampler.callback_state = cc_callback
    on_script_unloaded(restore_callback)
    on_ui_settings(settings)
