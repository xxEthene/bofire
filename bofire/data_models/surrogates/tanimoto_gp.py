from typing import Literal

from pydantic import Field, validator

from bofire.data_models.kernels.api import AnyKernel, ScaleKernel, AnyMolecularKernel
from bofire.data_models.kernels.molecular import TanimotoKernel
from bofire.data_models.priors.api import (
    BOTORCH_NOISE_PRIOR,
    BOTORCH_SCALE_PRIOR,
    AnyPrior,
)
from bofire.data_models.surrogates.botorch import BotorchSurrogate
from bofire.data_models.surrogates.scaler import ScalerEnum
from bofire.data_models.surrogates.trainable import TrainableSurrogate

from bofire.data_models.molfeatures.api import *


class TanimotoGPSurrogate(BotorchSurrogate, TrainableSurrogate):
    type: Literal["TanimotoGPSurrogate"] = "TanimotoGPSurrogate"

    kernel: AnyMolecularKernel = Field(
        default_factory=lambda: ScaleKernel(
            base_kernel=TanimotoKernel(
                ard=True,
            ),
            outputscale_prior=BOTORCH_SCALE_PRIOR(),
        )
    )
    noise_prior: AnyPrior = Field(default_factory=lambda: BOTORCH_NOISE_PRIOR())
    scaler: ScalerEnum = ScalerEnum.IDENTITY

    # TanimotoGP will be used when at least one of fingerprints, fragments, or fingerprintsfragments are present
    @validator("input_preprocessing_specs")
    def validate_moleculars(cls, v, values):
        """Checks that at least one of fingerprints, fragments, or fingerprintsfragments features are present."""
        if not any (
            [isinstance(value, Fingerprints)
            or isinstance(value, Fragments)
            or isinstance(value, FingerprintsFragments)
            for value in v.values()
            ]
        ):
            raise ValueError(
                "MixedTanimotoGPSurrogate can only be used if at least one of fingerprints, fragments, or fingerprintsfragments features are present."
            )
        return v