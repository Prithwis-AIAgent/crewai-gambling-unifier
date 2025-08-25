from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from gambling_unifier.tools.custom_tool import (
    ScrapePolymarketTool,
    ScrapeKalshiTool,
    ScrapePredictionMarketTool,
    BrowserScrapeTool,
    MatchProductsTool,
    ToCSVTool,
)
from gambling_unifier.tools.rag_tool import RAGChatTool


@CrewBase
class GamblingUnifier():
    """GamblingUnifier crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

   
    @agent
    def researcher(self) -> Agent:
        llm = LLM(model="gpt-5-mini")
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            llm=llm,
            tools=[
                ScrapePolymarketTool(),
                ScrapeKalshiTool(),
                ScrapePredictionMarketTool(),
                BrowserScrapeTool(),
            ],
        )

    @agent
    def reporting_analyst(self) -> Agent:
        llm = LLM(model="gpt-5-mini")
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True,
            llm=llm,
            tools=[MatchProductsTool(), ToCSVTool()],
        )

    @agent
    def csv_producer(self) -> Agent:
        llm = LLM(model="gpt-5-mini")
        return Agent(
            config=self.agents_config['csv_producer'], # type: ignore[index]
            verbose=True,
            llm=llm,
            tools=[ToCSVTool()],
        )

    @agent
    def rag_chat_agent(self) -> Agent:
        llm = LLM(model="gpt-5-mini")
        return Agent(
            config=self.agents_config['rag_chat_agent'], # type: ignore[index]
            verbose=True,
            llm=llm,
            tools=[RAGChatTool()],
        )

   
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def csv_task(self) -> Task:
        return Task(
            config=self.tasks_config['csv_task'], # type: ignore[index]
            output_file='unified_products.csv'
        )

    @task
    def rag_chat_task(self) -> Task:
        return Task(
            config=self.tasks_config['rag_chat_task'], # type: ignore[index]
            output_file='rag_chat_output.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GamblingUnifier crew"""
      

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            
        )
