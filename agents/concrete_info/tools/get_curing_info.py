"""Tool for retrieving information about concrete curing techniques."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def get_curing_info(
    ctx: Context,
    curing_method: str = "general",
    environmental_conditions: str = "normal"
) -> str:
    """Retrieves detailed information about concrete curing techniques and best practices.
    
    Args:
        curing_method: The specific curing method to get information about
        environmental_conditions: Environmental conditions affecting curing (hot, cold, normal)
    """
    ctx.write_event_to_stream(ProgressEvent(msg=f"Retrieving information about {curing_method} curing in {environmental_conditions} conditions"))
    
    # In a production system, this would query a technical database
    # For this example, we'll return predefined information
    
    curing_info = {
        "general": {
            "normal": "Concrete curing is the process of maintaining adequate moisture and temperature conditions for a sufficient "
                     "period to allow the concrete to achieve desired properties. Proper curing can significantly improve strength, "
                     "durability, and wear resistance. Curing should begin as soon as the concrete has set enough to prevent surface damage, "
                     "typically 1-2 hours after finishing, and should continue for at least 7 days for standard mixes.",
            "hot": "In hot weather (above 85°F/29°C), special precautions are needed to prevent rapid moisture loss. "
                  "Begin curing immediately after finishing. Use sunshades, windbreaks, and fog sprays before and during "
                  "placement. Consider working at night. Use ice in mixing water or liquid nitrogen to cool the concrete. "
                  "Apply curing compound at twice the normal rate or use wet curing with continuous moisture.",
            "cold": "In cold weather (below 40°F/4°C), concrete sets more slowly and may freeze before developing sufficient strength. "
                   "Use heated enclosures or insulating blankets to maintain temperature. Use Type III (high-early-strength) cement "
                   "or accelerating admixtures. Never place concrete on frozen ground. Maintain temperature above 50°F/10°C for at "
                   "least 3 days for normal concrete and 2 days for high-early-strength concrete."
        },
        "water": {
            "normal": "Water curing involves keeping concrete continuously wet by ponding, spraying, or covering with water-retaining "
                     "materials like burlap or cotton mats. This method provides excellent curing by supplying additional water to replace "
                     "that lost through evaporation. It's highly effective but labor-intensive. Keep concrete continuously wet for 7 days "
                     "for normal concrete and 3 days for high-early-strength concrete.",
            "hot": "In hot weather, water curing is especially beneficial. Use continuous water spraying or ponding. If using wet coverings, "
                  "they must be kept continuously wet, which may require attention every 1-2 hours. Add ice to ponded water if needed to "
                  "control concrete temperature. Nighttime sprinkling may be insufficient - continuous moisture is essential.",
            "cold": "Water curing is generally not recommended in freezing temperatures unless the water and concrete can be kept above "
                   "freezing. If used, the water temperature should not be more than 20°F/11°C cooler than the concrete surface to avoid "
                   "thermal shock."
        },
        "membrane": {
            "normal": "Membrane curing uses liquid-applied compounds that form a water-retentive film over the concrete. Apply as soon as "
                     "bleeding has stopped and surface water has disappeared. Apply uniformly according to manufacturer's recommended coverage "
                     "rate, typically 150-200 sq ft per gallon. For vertical surfaces, apply immediately after removing forms.",
            "hot": "In hot weather, apply membrane compounds at 1.5 to 2 times the normal rate. Consider using white-pigmented curing "
                  "compounds to reflect heat. Apply as soon as surface water has disappeared, but while the surface still has a sheen. "
                  "A second application may be necessary under extreme conditions.",
            "cold": "Membrane curing compounds are less effective in cold weather due to slower chemical reaction and film formation. "
                   "They're not recommended when temperatures are below 40°F/4°C. If used in cool weather, allow for longer setting times "
                   "before application."
        }
    }
    
    method_key = curing_method.lower()
    condition_key = environmental_conditions.lower()
    
    if method_key in curing_info:
        if condition_key in curing_info[method_key]:
            return curing_info[method_key][condition_key]
        else:
            return curing_info[method_key]["normal"]
    else:
        available_methods = ", ".join([key for key in curing_info.keys()])
        return f"Information about {curing_method} curing is not available. Available topics include {available_methods}."
