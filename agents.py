from crewai import Agent
from tools import any_website_tool

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create a senior travel content researcher
travel_itinerary_researcher = Agent(
    role="Travel Itinerary Researcher",
    goal=(
        "Research and extract valuable insights about {question} travel itineraries from reliable websites, "
        "focusing on destinations, day-wise activities, accommodations, and tips for creating engaging travel plans."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "An expert in exploring travel-related content from websites, skilled in identifying the best places to visit, "
        "building detailed day-by-day itineraries, and providing actionable insights for travelers."
    ),
    tools=[any_website_tool],  # Replace this with appropriate web scraping or content extraction tools
    allow_delegation=True,
)

# Create a senior travel itinerary writer
travel_itinerary_writer = Agent(
    role="Travel Itinerary Writer",
    goal=(
        "Craft structured, detailed, and engaging travel itineraries for {question} based on the extracted insights, "
        "focusing on providing clear travel plans and practical advice for a seamless experience."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "A seasoned travel planner specializing in creating day-by-day itineraries. Your goal is to organize "
        "travel plans into detailed schedules, including must-visit destinations, activities, transportation options, "
        "and accommodation recommendations."
    ),
    tools=[any_website_tool],  # Replace or extend with relevant tools for drafting and formatting itineraries
    allow_delegation=False,
)
