"""Tool for retrieving general information about concrete fabrication."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def get_fabrication_info(
    ctx: Context,
    topic: str,
    application_type: str = "general"
) -> str:
    """Retrieves general information about concrete fabrication processes.
    
    Args:
        topic: The specific aspect of concrete fabrication to retrieve information about
        application_type: The type of application (residential, commercial, industrial)
    """
    ctx.write_event_to_stream(ProgressEvent(msg=f"Retrieving information about {topic} for {application_type} applications"))
    
    # In a production system, this would query a database or knowledge base
    # For this example, we'll return predefined information
    
    concrete_info = {
        "mixing": {
            "general": "Concrete mixing involves combining cement, aggregates, water, and sometimes additives in precise proportions. "
                      "The process typically involves dry mixing the cement and aggregates first, then gradually adding water.",
            "residential": "For residential applications, concrete is typically mixed in smaller batches, often using a drum mixer or by hand. "
                          "Standard ratio is 1 part cement, 2 parts sand, and 3 parts gravel with sufficient water for workability.",
            "commercial": "Commercial concrete mixing usually involves ready-mix concrete delivered by trucks. "
                         "The mix is designed for specific strength requirements and often includes additives for performance.",
            "industrial": "Industrial concrete applications require specialized mixes with enhanced properties like chemical resistance, "
                         "high strength, or rapid setting. These often use specialized cements and precise mixing conditions."
        },
        "pouring": {
            "general": "Concrete pouring should be done continuously when possible, starting from one corner and moving systematically. "
                      "The concrete should be poured as close as possible to its final position to avoid segregation.",
            "residential": "For residential slabs, pour concrete starting from the farthest corner and work backward. "
                          "Use a straight edge to strike off excess concrete and create a level surface.",
            "commercial": "Commercial pours often use pump trucks to deliver concrete precisely where needed. "
                         "For large slabs, contraction joints should be planned every 10-15 feet.",
            "industrial": "Industrial floors often require specialized pouring techniques like laser screed leveling "
                         "and may incorporate fiber reinforcement throughout the pour."
        },
        "finishing": {
            "general": "Concrete finishing involves creating the desired surface texture after pouring. "
                      "Common techniques include floating, troweling, brooming, and edging.",
            "residential": "Residential concrete is often finished with a light broom texture for driveways or "
                          "a smooth trowel finish for interior slabs that will receive flooring.",
            "commercial": "Commercial floors may require burnished finishes for durability or special textures "
                         "for slip resistance in wet areas.",
            "industrial": "Industrial floors often receive power-troweled finishes for maximum durability and "
                         "may include surface hardeners or sealers applied during the finishing process."
        }
    }
    
    if topic.lower() in concrete_info and application_type.lower() in concrete_info[topic.lower()]:
        return concrete_info[topic.lower()][application_type.lower()]
    elif topic.lower() in concrete_info:
        return concrete_info[topic.lower()]["general"]
    else:
        return f"Information about {topic} is not available. Available topics include mixing, pouring, and finishing."
