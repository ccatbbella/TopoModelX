"""Template Layer with two conv passing steps."""
import torch

from topomodelx.base.conv import Conv


class TemplateLayer(torch.nn.Module):
    """Template Layer with two conv passing steps.
    We show how to

    Parameters
    ----------
    in_channels : int
        Dimension of input features.
    out_channels : int
        Dimension of output features.
    aggr_func : string
        Aggregation method.
        (Inter-neighborhood).
    """

    def __init__(
        self,
        in_channels,
        intermediate_channels,
        out_channels,
        incidence_2,
    ):
        super().__init__()
        self.incidence_2 = incidence_2

        incidence_2_transpose = incidence_2.to_dense().T.to_sparse()

        self.conv_level1_2_to_1 = Conv(
            in_channels=in_channels,
            out_channels=intermediate_channels,
            neighborhood=incidence_2,
            aggr_norm=True,
            update_func="sigmoid",
        )
        self.conv_level2_1_to_2 = Conv(
            in_channels=intermediate_channels,
            out_channels=out_channels,
            neighborhood=incidence_2_transpose,
            aggr_norm=True,
            update_func="sigmoid",
        )

    def reset_parameters(self):
        r"""Reset learnable parameters."""
        self.conv_level1_2_to_1.reset_parameters()
        self.conv_level2_1_to_2.reset_parameters()

    def forward(self, x):
        r"""Forward computation.

        Parameters
        ----------
        x : torch.tensor, shape=[n_faces, in_channels]
            Input features on the faces of the simplicial complex.

        Returns
        -------
        x : torch.tensor, shape=[n_faces, out_channels]
        """
        if x.shape[-2] != self.incidence_2.shape[-1]:
            raise ValueError(
                f"Shape of input face features does not have the correct number of faces {self.incidence_2.shape[-1]}."
            )
        x_edges = self.conv_level1_2_to_1(x)
        x = self.conv_level2_1_to_2(x_edges)
        return x
