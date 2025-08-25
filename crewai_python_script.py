#!/usr/bin/env python3
"""
Gambling Unifier - CrewAI Implementation
A comprehensive system that unifies gambling products from multiple prediction markets
using a multi-agent crew approach.

This script demonstrates:
- Multi-agent collaboration for data collection and analysis
- Web scraping tools for gambling market data
- Product matching and unification across platforms
- CSV generation and reporting
- RAG-based query system for insights

Author: [Prithwis Das]
Date: [26/08/2025]
"""

import os
import sys
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI

# Custom imports
from src.gambling_unifier.tools.custom_tool import (
    ScrapePolymarketTool,
    ScrapeKalshiTool,
    ScrapePredictionMarketTool,
    BrowserScrapeTool,
    MatchProductsTool,
    ToCSVTool,
)
from src.gambling_unifier.tools.rag_tool import RAGChatTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gambling_unifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GamblingProduct:
    """Data structure for gambling products"""
    site: str
    product_id: str
    name: str
    price: Optional[float]
    url: str
    confidence: Optional[float] = None

class GamblingUnifierCrew:
    """
    Main CrewAI implementation for unifying gambling products across multiple platforms
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the Gambling Unifier Crew
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
        """
        self.api_key = api_key
        self.model = model
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1
        )
        
        # Initialize tools
        self.tools = {
            'polymarket': ScrapePolymarketTool(),
            'kalshi': ScrapeKalshiTool(),
            'prediction_market': ScrapePredictionMarketTool(),
            'browser': BrowserScrapeTool(),
            'matcher': MatchProductsTool(),
            'csv_tool': ToCSVTool(),
            'rag': RAGChatTool()
        }
        
        # Create output directory
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Gambling Unifier Crew initialized successfully")
    
    def create_researcher_agent(self) -> Agent:
        """Create the data collection agent"""
        return Agent(
            role="Gambling Data Collector",
            goal="Scrape gambling/prediction market websites and return unified JSON arrays of products",
            backstory="""You are an expert web data collector specializing in gambling and prediction markets. 
            You know how to call tools to fetch JSON or parse HTML safely and return structured product records 
            including name, product_id, price, site, and url. You're thorough and ensure data quality.""",
            tools=[
                self.tools['polymarket'],
                self.tools['kalshi'],
                self.tools['prediction_market'],
                self.tools['browser']
            ],
            llm=self.llm,
            verbose=True
        )
    
    def create_analyst_agent(self) -> Agent:
        """Create the analysis and unification agent"""
        return Agent(
            role="Product Unifier & Analyst",
            goal="Identify which products are the same across sites, compute confidence, and generate unified data",
            backstory="""You specialize in entity resolution and data analysis. You take raw product records from 
            multiple sources, match them with fuzzy similarity algorithms, and output a concise, analysis-ready 
            dataset. You're skilled at identifying patterns and anomalies in gambling markets.""",
            tools=[
                self.tools['matcher'],
                self.tools['csv_tool']
            ],
            llm=self.llm,
            verbose=True
        )
    
    def create_csv_agent(self) -> Agent:
        """Create the CSV generation agent"""
        return Agent(
            role="CSV Writer & Data Exporter",
            goal="Convert unified product groups into clean, formatted CSV files with proper structure",
            backstory="""You are focused on data formatting and export reliability. You ensure that CSV files 
            are properly structured, contain all required columns, and are ready for analysis. You maintain 
            data integrity and formatting standards.""",
            tools=[self.tools['csv_tool']],
            llm=self.llm,
            verbose=True
        )
    
    def create_rag_agent(self) -> Agent:
        """Create the RAG query agent"""
        return Agent(
            role="RAG Chat Assistant",
            goal="Answer questions about unified gambling products using the generated data and reports",
            backstory="""You are a helpful assistant that can analyze and answer questions about gambling markets 
            and products by searching through the unified data and providing insights. You help users understand 
            market trends, pricing patterns, and product comparisons.""",
            tools=[self.tools['rag']],
            llm=self.llm,
            verbose=True
        )
    
    def create_research_task(self) -> Task:
        """Create the data collection task"""
        return Task(
            description="""Use the scraping tools to retrieve product lists from at least three gambling/prediction 
            market sites:
            1. Polymarket API or markets page
            2. Kalshi catalog or markets page  
            3. prediction-market.com or other alternatives
            
            Return a single JSON array combining all products with fields: site, product_id, name, price, url.
            Ensure data quality and handle any errors gracefully.""",
            expected_output="""A JSON array of product records with fields: site, product_id, name, 
            price (float|nullable), url. The data should be clean and ready for analysis.""",
            agent=self.create_researcher_agent(),
            output_file=str(self.output_dir / 'raw_products.json')
        )
    
    def create_analysis_task(self) -> Task:
        """Create the product unification task"""
        return Task(
            description="""Take the JSON array of products from the previous task. Use the matching tool to 
            group same products across sites and compute confidence values. Then convert the groups to CSV 
            with columns: name, site, product_id, price, confidence. Also write a brief markdown news-style 
            summary describing notable differences in pricing and interesting markets.""",
            expected_output="""1) CSV content for unified product board with proper columns. 
            2) A short markdown review highlighting key insights and market patterns.""",
            agent=self.create_analyst_agent(),
            output_file=str(self.output_dir / 'unified_products.csv'),
            context=[self.create_research_task()]
        )
    
    def create_csv_task(self) -> Task:
        """Create the CSV generation task"""
        return Task(
            description="""Receive the unified product groups and convert them to a properly formatted CSV file 
            with the columns: name, site, product_id, price, confidence. Ensure the CSV is clean, well-structured, 
            and ready for analysis. Handle any data formatting issues.""",
            expected_output="""A clean, well-formatted CSV file with all required columns and proper data types. 
            The file should be ready for import into analysis tools.""",
            agent=self.create_csv_agent(),
            output_file=str(self.output_dir / 'final_products.csv'),
            context=[self.create_analysis_task()]
        )
    
    def create_rag_task(self) -> Task:
        """Create the RAG query task"""
        return Task(
            description="""Answer a sample question about the unified gambling products using the RAG tool. 
            The question should be about analyzing the data, finding patterns, or getting insights from the 
            unified product board. Demonstrate the system's ability to provide meaningful analysis.""",
            expected_output="""A detailed answer to the question based on the available data, demonstrating 
            the RAG system's ability to provide insights about the gambling products and market trends.""",
            agent=self.create_rag_agent(),
            output_file=str(self.output_dir / 'rag_analysis.md'),
            context=[self.create_csv_task()]
        )
    
    def create_crew(self) -> Crew:
        """Create and configure the main crew"""
        return Crew(
            agents=[
                self.create_researcher_agent(),
                self.create_analyst_agent(),
                self.create_csv_agent(),
                self.create_rag_agent()
            ],
            tasks=[
                self.create_research_task(),
                self.create_analysis_task(),
                self.create_csv_task(),
                self.create_rag_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete gambling unifier workflow
        
        Returns:
            Dictionary containing results and output file paths
        """
        try:
            logger.info("Starting Gambling Unifier Crew execution...")
            
            # Create and run the crew
            crew = self.create_crew()
            result = crew.kickoff()
            
            logger.info("Crew execution completed successfully")
            
            # Collect output information
            outputs = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'output_files': {
                    'raw_products': str(self.output_dir / 'raw_products.json'),
                    'unified_products': str(self.output_dir / 'unified_products.csv'),
                    'final_products': str(self.output_dir / 'final_products.csv'),
                    'rag_analysis': str(self.output_dir / 'rag_analysis.md')
                },
                'result': result
            }
            
            # Save results summary
            with open(self.output_dir / 'execution_summary.json', 'w') as f:
                json.dump(outputs, f, indent=2)
            
            logger.info(f"Execution summary saved to {self.output_dir / 'execution_summary.json'}")
            return outputs
            
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}")
            raise
    
    def interactive_chat(self):
        """Interactive chat interface using the RAG system"""
        print("🤖 Gambling Unifier RAG Chat Interface")
        print("=" * 50)
        print("Ask questions about the unified gambling products!")
        print("Type 'quit' to exit")
        print()
        
        rag_agent = self.create_rag_agent()
        
        while True:
            try:
                question = input("You: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                if not question:
                    continue
                
                print("\n🤖 Analyzing your question...")
                
                # Create a simple task for the question
                chat_task = Task(
                    description=f"Answer this question: {question}",
                    agent=rag_agent
                )
                
                result = chat_task.execute()
                print(f"\n🤖 {result}")
                print("\n" + "-" * 50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Try asking a different question.")

def main():
    """Main execution function"""
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key and try again.")
        return
    
    try:
        # Initialize the crew
        crew = GamblingUnifierCrew(api_key=api_key)
        
        # Run the main workflow
        print("🚀 Starting Gambling Unifier Crew...")
        results = crew.run()
        
        print("\n✅ Workflow completed successfully!")
        print(f"📁 Output files saved to: {crew.output_dir}")
        
        # Show output files
        for name, path in results['output_files'].items():
            if Path(path).exists():
                print(f"   📄 {name}: {path}")
        
        # Offer interactive chat
        print("\n💬 Would you like to chat with the RAG system? (y/n)")
        if input().lower().startswith('y'):
            crew.interactive_chat()
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
