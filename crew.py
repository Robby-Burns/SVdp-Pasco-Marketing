import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	SerperDevTool,
	ScrapeWebsiteTool,
	FileReadTool,
	WebsiteSearchTool,
	QdrantVectorSearchTool
)
from st_vincent_de_paul_smart_content_marketing_automation.tools.facebook_publishing_tool import FacebookPublishingTool
from st_vincent_de_paul_smart_content_marketing_automation.tools.squarespace_publishing_tool import SquarespacePublishingTool
from st_vincent_de_paul_smart_content_marketing_automation.tools.pinecone_storage_tool import PineconeStorageTool

from crewai_tools import CrewaiEnterpriseTools



@CrewBase
class StVincentDePaulSmartContentMarketingAutomationCrew:
    """StVincentDePaulSmartContentMarketingAutomation crew"""

    
    @agent
    def story_database_manager(self) -> Agent:
        enterprise_actions_tool = CrewaiEnterpriseTools(
            actions_list=[
                
                "google_sheets_get_values",
                
                "google_sheets_update_values",
                
            ],
        )

        
        return Agent(
            config=self.agents_config["story_database_manager"],
            
            
            tools=[
				SerperDevTool(),
				ScrapeWebsiteTool(),
				FileReadTool(),
				*enterprise_actions_tool
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def content_creator(self) -> Agent:

        
        embedding_config_websitesearchtool = dict(
            llm=dict(
                provider="",
                config=dict(
                    model="",
                ),
            ),
            embedder=dict(
                provider="",
                config=dict(
                    model="",
                ),
            ),
        )
        
        return Agent(
            config=self.agents_config["content_creator"],
            
            
            tools=[
				WebsiteSearchTool(config=embedding_config_websitesearchtool)
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def brand_compliance_officer(self) -> Agent:

        
        return Agent(
            config=self.agents_config["brand_compliance_officer"],
            
            
            tools=[

            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def approval_manager(self) -> Agent:
        enterprise_actions_tool = CrewaiEnterpriseTools(
            actions_list=[
                
                "microsoft_outlook_send_email",
                
                "microsoft_outlook_get_messages",
                
            ],
        )

        
        return Agent(
            config=self.agents_config["approval_manager"],
            
            
            tools=[
				*enterprise_actions_tool
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def publishing_coordinator(self) -> Agent:

        
        return Agent(
            config=self.agents_config["publishing_coordinator"],
            
            
            tools=[
				FacebookPublishingTool(),
				SquarespacePublishingTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def performance_analytics_manager(self) -> Agent:

        
        embedding_config_websitesearchtool = dict(
            llm=dict(
                provider="",
                config=dict(
                    model="",
                ),
            ),
            embedder=dict(
                provider="",
                config=dict(
                    model="",
                ),
            ),
        )
        
        return Agent(
            config=self.agents_config["performance_analytics_manager"],
            
            
            tools=[
				WebsiteSearchTool(config=embedding_config_websitesearchtool),
				ScrapeWebsiteTool(),
				QdrantVectorSearchTool(),
				PineconeStorageTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def retrieve_optimal_story_from_excel_database(self) -> Task:
        return Task(
            config=self.tasks_config["retrieve_optimal_story_from_excel_database"],
            markdown=False,
            
            
        )
    
    @task
    def research_high_performance_content_patterns(self) -> Task:
        return Task(
            config=self.tasks_config["research_high_performance_content_patterns"],
            markdown=False,
            
            
        )
    
    @task
    def generate_facebook_content(self) -> Task:
        return Task(
            config=self.tasks_config["generate_facebook_content"],
            markdown=False,
            
            
        )
    
    @task
    def generate_blog_content(self) -> Task:
        return Task(
            config=self.tasks_config["generate_blog_content"],
            markdown=False,
            
            
        )
    
    @task
    def brand_compliance_review(self) -> Task:
        return Task(
            config=self.tasks_config["brand_compliance_review"],
            markdown=False,
            
            
        )
    
    @task
    def send_approval_request(self) -> Task:
        return Task(
            config=self.tasks_config["send_approval_request"],
            markdown=False,
            
            
        )
    
    @task
    def publish_approved_content(self) -> Task:
        return Task(
            config=self.tasks_config["publish_approved_content"],
            markdown=False,
            
            
        )
    
    @task
    def track_performance_and_store_in_pinecone(self) -> Task:
        return Task(
            config=self.tasks_config["track_performance_and_store_in_pinecone"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the StVincentDePaulSmartContentMarketingAutomation crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
