# Copyright 2022 The Plenoptix Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Collection of render heads
"""
from enum import Enum
from typing import Optional

from torch import nn
from torchtyping import TensorType

from pyrad.fields.modules.base import FieldModule


class FieldHeadNames(Enum):
    """Possible field outputs"""

    RGB = "rgb"
    SH = "sh"
    DENSITY = "density"
    UNCERTAINTY = "uncertainty"
    TRANSIENT_RGB = "transient_rgb"
    TRANSIENT_DENSITY = "transient_density"
    SEMANTICS = "semantics"


class FieldHead(FieldModule):
    """Base field output

    Args:
        out_dim (int): output dimension for renderer
        field_head_name (FieldHeadNames): Field type
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(
        self,
        out_dim: int,
        field_head_name: FieldHeadNames,
        in_dim: Optional[int] = None,
        activation: Optional[nn.Module] = None,
    ) -> None:

        super().__init__()
        self.out_dim = out_dim
        self.activation = activation
        self.field_head_name = field_head_name
        self.net = None
        if in_dim is not None:
            self.in_dim = in_dim
            self._construct_net()

    def set_in_dim(self, in_dim: int) -> None:
        """Set input dimension of Field Head"""
        self.in_dim = in_dim
        self._construct_net()

    def _construct_net(self):
        layers = [nn.Linear(self.in_dim, self.out_dim)]
        if self.activation:
            layers.append(self.activation)
        self.net = nn.Sequential(*layers)

    def forward(self, in_tensor: TensorType[..., "in_dim"]) -> TensorType:
        """Process network output for renderer

        Args:
            in_tensor (TensorType[..., "in_dim]): Network input

        Returns:
            TensorType[..., "out_dim"]: Render head output
        """
        if not self.net:
            raise SystemError("in_dim not set. Must be provided to construtor, or set_in_dim() should be called.")
        out_tensor = self.net(in_tensor)
        return out_tensor


class DensityFieldHead(FieldHead):
    """Density output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, in_dim: Optional[int] = None, activation: Optional[nn.Module] = nn.Softplus()) -> None:
        super().__init__(in_dim=in_dim, out_dim=1, field_head_name=FieldHeadNames.DENSITY, activation=activation)


class RGBFieldHead(FieldHead):
    """RGB output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, in_dim: Optional[int] = None, activation: Optional[nn.Module] = nn.Sigmoid()) -> None:
        super().__init__(in_dim=in_dim, out_dim=3, field_head_name=FieldHeadNames.RGB, activation=activation)


class SHFieldHead(FieldHead):
    """Spherical harmonics output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        levels (int, optional): Number of spherical harmonics layers. Defaults to 3.
        channels (int, optional): Number of channels. Defaults to 3 (ie RGB).
        activation (Optional[nn.Module], optional): Output activation. Defaults to None.
    """

    def __init__(
        self, in_dim: Optional[int] = None, levels: int = 3, channels: int = 3, activation: Optional[nn.Module] = None
    ) -> None:

        out_dim = channels * levels**2
        super().__init__(in_dim=in_dim, out_dim=out_dim, field_head_name=FieldHeadNames.SH, activation=activation)


class UncertaintyFieldHead(FieldHead):
    """Uncertainty output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, in_dim: Optional[int] = None, activation: Optional[nn.Module] = nn.Softplus()) -> None:
        super().__init__(in_dim=in_dim, out_dim=1, field_head_name=FieldHeadNames.UNCERTAINTY, activation=activation)


class TransientRGBFieldHead(FieldHead):
    """Transient RGB output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, in_dim: Optional[int] = None, activation: Optional[nn.Module] = nn.Sigmoid()) -> None:
        super().__init__(in_dim=in_dim, out_dim=3, field_head_name=FieldHeadNames.TRANSIENT_RGB, activation=activation)


class TransientDensityFieldHead(FieldHead):
    """Transient density output

    Args:
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, in_dim: Optional[int] = None, activation: Optional[nn.Module] = nn.Softplus()) -> None:
        super().__init__(
            in_dim=in_dim, out_dim=1, field_head_name=FieldHeadNames.TRANSIENT_DENSITY, activation=activation
        )


class SemanticFieldHead(FieldHead):
    """Semantic stuff output

    Args:
        num_classes (int): Number of semantic classes
        in_dim (int, optional): input dimension. If not defined in constructor, it must be set later.
        activation (Optional[nn.Module]): output head activation
    """

    def __init__(self, num_classes: int, in_dim: Optional[int] = None) -> None:
        super().__init__(in_dim=in_dim, out_dim=num_classes, field_head_name=FieldHeadNames.SEMANTICS, activation=None)