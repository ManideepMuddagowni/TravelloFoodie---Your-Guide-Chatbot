from crewai_tools import WebsiteSearchTool, SerperDevTool



# Example of initiating tool that agents can use 
# to search across any discovered websites

any_website_tool = WebsiteSearchTool()




specific_website_tool = WebsiteSearchTool(website='https://example.com')
