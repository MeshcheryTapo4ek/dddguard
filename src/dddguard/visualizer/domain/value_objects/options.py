from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class VisualizationOptions:
    """
    Configuration flags for the rendering engine.
    """
    # Visibility
    show_errors: bool = True

    # Graph Filtering (Split Logic)
    hide_root_arrows: bool = True
    hide_shared_arrows: bool = True

    # Output
    output_file: str = "architecture.drawio"