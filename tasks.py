from crewai import Task
from tools import any_website_tool
from agents import travel_itinerary_researcher, travel_itinerary_writer

## Research Task
travel_itinerary_research_task = Task(
  description=(
    """You are a highly skilled travel researcher specializing in finding the best places to visit and crafting detailed travel itineraries. 
       Your goal is to assist in gathering valuable insights for the topic {question} from websites, 
       focusing on destinations, attractions, and travel plans."""
  ),
  expected_output=""" Present detailed recommendations for must-visit places, activities, and 
                    any notable travel tips, including suggested day-wise plans based on the {question}.""",
  tools=[any_website_tool],
  agent=travel_itinerary_researcher,
)

# Writing task with language model configuration
travel_itinerary_write_task = Task(
  description=(
    "get the info from the website on the topic {question}."
  ),
  expected_output="""Present detailed recommendations for must-visit places, activities, and 
                    any notable travel tips, including suggested day-wise plans based on the {question}.""",
  tools=[any_website_tool],
  agent=travel_itinerary_writer,
  async_execution=False,
  output_file='new-travel-itinerary-post.md'  # Example of output customization
)