from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DrawOptionsDto:
    """
    Driving DTO: Represents the user's choices from the UI.
    """
    # Visibility Toggles 
    show_errors: bool = True
    
    # Directional Filters
    hide_root_arrows: bool = True    # Hide arrows FROM Root (Wiring noise)
    hide_shared_arrows: bool = True  # Hide arrows TO Shared (Usage noise)
    
    # Output
    output_file: str = "architecture.drawio"