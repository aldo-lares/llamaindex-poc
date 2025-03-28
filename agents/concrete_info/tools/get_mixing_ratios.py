"""Tool for retrieving concrete mixing ratios."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def get_mixing_ratios(
    ctx: Context,
    strength_requirement: str,
    application: str = "general"
) -> str:
    """Retrieves recommended mixing ratios for concrete based on strength requirements and application.
    
    Args:
        strength_requirement: The strength requirement (low, medium, high, very high)
        application: The intended application for the concrete
    """
    ctx.write_event_to_stream(ProgressEvent(msg=f"Retrieving mixing ratios for {strength_requirement} strength concrete for {application}"))
    
    # In a production system, this would query a technical database
    # For this example, we'll return predefined information
    
    mixing_ratios = {
        "low": {
            "ratio": "1:3:6 (cement:sand:aggregate)",
            "water_cement_ratio": "0.55-0.60",
            "strength": "10-15 MPa (1450-2175 psi)",
            "applications": "Footpaths, garden paths, and non-structural elements",
            "notes": "Economical mix for non-load bearing applications"
        },
        "medium": {
            "ratio": "1:2:4 (cement:sand:aggregate)",
            "water_cement_ratio": "0.45-0.55",
            "strength": "20-25 MPa (2900-3625 psi)",
            "applications": "Residential foundations, driveways, patios",
            "notes": "Standard mix for general construction"
        },
        "high": {
            "ratio": "1:1.5:3 (cement:sand:aggregate)",
            "water_cement_ratio": "0.40-0.45",
            "strength": "30-35 MPa (4350-5075 psi)",
            "applications": "Commercial floors, beams, columns, water-retaining structures",
            "notes": "Higher cement content for structural applications"
        },
        "very high": {
            "ratio": "1:1:2 (cement:sand:aggregate)",
            "water_cement_ratio": "0.35-0.40",
            "strength": "40+ MPa (5800+ psi)",
            "applications": "High-rise buildings, bridges, heavy industrial floors",
            "notes": "May require admixtures and careful curing for best results"
        }
    }
    
    strength_key = strength_requirement.lower()
    if strength_key in mixing_ratios:
        ratio_info = mixing_ratios[strength_key]
        
        response = f"## Mixing Ratio for {strength_requirement.capitalize()} Strength Concrete\n\n"
        response += f"- **Basic Ratio**: {ratio_info['ratio']}\n"
        response += f"- **Water-Cement Ratio**: {ratio_info['water_cement_ratio']}\n"
        response += f"- **Expected Strength**: {ratio_info['strength']}\n"
        response += f"- **Common Applications**: {ratio_info['applications']}\n"
        response += f"- **Notes**: {ratio_info['notes']}\n\n"
        
        if application != "general":
            response += f"For {application} specifically, "
            if application.lower() in ["driveways", "patios", "sidewalks"]:
                response += "consider adding air-entraining admixtures if in freeze-thaw environments. "
                response += "A slightly lower water content can improve durability for exterior applications."
            elif application.lower() in ["foundations", "footings", "slabs"]:
                response += "ensure proper reinforcement is used and consider waterproofing additives if needed. "
                response += "Proper compaction is essential for these structural elements."
            elif application.lower() in ["countertops", "decorative"]:
                response += "use smaller aggregate sizes (3/8\" maximum) for a smoother finish. "
                response += "Consider using white cement and pigments for decorative applications."
        
        return response
    else:
        return f"Information for '{strength_requirement}' strength is not available. Please choose from low, medium, high, or very high."
