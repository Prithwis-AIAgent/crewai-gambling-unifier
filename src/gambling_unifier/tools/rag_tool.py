from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
import os
import logging

logger = logging.getLogger('gambling_unifier.rag')


class RAGChatInput(BaseModel):
    question: str = Field(..., description="Question about the unified gambling products")


class RAGChatTool(BaseTool):
    name: str = "rag_chat"
    description: str = (
        "Answer questions about the unified gambling products by searching through the generated CSV and report files."
    )
    args_schema: Type[BaseModel] = RAGChatInput

    def _run(self, question: str) -> str:
        try:
            csv_path = "unified_products.csv"
            report_path = "report.md"

            knowledge = []
            logger.info("RAG query started")

            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    knowledge.append(f"CSV Data:\n{df.to_string()}")
                    logger.info(f"Loaded CSV with {len(df)} rows")
                except Exception as e:
                    logger.error(f"CSV loading error: {e}")
                    knowledge.append(f"CSV loading error: {e}")
            else:
                logger.warning("CSV file not found")

            if os.path.exists(report_path):
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        knowledge.append(f"Report:\n{content}")
                        logger.info(f"Loaded report with {len(content)} chars")
                except Exception as e:
                    logger.error(f"Report loading error: {e}")
                    knowledge.append(f"Report loading error: {e}")
            else:
                logger.warning("Report file not found")

            if not knowledge:
                logger.error("No knowledge files found")
                return "No knowledge files found. Please run the main crew first to generate the CSV and report."

            question_lower = question.lower()
            relevant_info = []

            for k in knowledge:
                if any(word in k.lower() for word in question_lower.split()):
                    relevant_info.append(k)

            if not relevant_info:
                relevant_info = knowledge

            context = "\n\n".join(relevant_info)

            if "most common" in question_lower or "common" in question_lower:
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        if 'site' in df.columns:
                            site_counts = df['site'].value_counts()
                            most_common_site = site_counts.index[0] if len(site_counts) > 0 else "No data"
                            answer = f"Based on the data, the most common site is: {most_common_site} with {site_counts.iloc[0] if len(site_counts) > 0 else 0} products."
                            logger.info("Answered: most common site")
                            return answer
                    except Exception as e:
                        logger.error(f"Most common calc failed: {e}")
                return f"Based on the available data:\n\n{context}\n\nFrom analyzing this data, I can see the information but need to examine the specific values to determine what's most common."

            elif "expensive" in question_lower or "price" in question_lower:
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        if 'price' in df.columns and df['price'].notna().any():
                            max_price = df['price'].max()
                            max_price_row = df.loc[df['price'].idxmax()]
                            answer = f"Based on the data, the most expensive market is: {max_price_row.get('name', 'Unknown')} with a price of {max_price} on {max_price_row.get('site', 'Unknown')}."
                            logger.info("Answered: most expensive market")
                            return answer
                    except Exception as e:
                        logger.error(f"Expensive market calc failed: {e}")
                return f"Based on the available data:\n\n{context}\n\nFrom analyzing this data, I can see pricing information but prices are empty; cannot determine most expensive markets."

            elif "confidence" in question_lower:
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        if 'confidence' in df.columns:
                            avg_confidence = df['confidence'].astype(float).mean()
                            high_conf_count = len(df[df['confidence'].astype(float) > 0.8])
                            answer = f"Based on the data, the average confidence level is: {avg_confidence:.2f}. There are {high_conf_count} products with high confidence (>0.8)."
                            logger.info("Answered: confidence stats")
                            return answer
                    except Exception as e:
                        logger.error(f"Confidence calc failed: {e}")
                return f"Based on the available data:\n\n{context}\n\nFrom analyzing this data, I can see confidence levels but need to examine the specific values to provide detailed statistics."

            logger.info("Answered: generic summary")
            return f"Based on the available data:\n\n{context}\n\nI've found relevant information for your question. The data shows various gambling markets across different sites with pricing and confidence information."

        except Exception as e:
            logger.exception("Unhandled RAG tool error")
            return f"RAG tool error: {e}"
