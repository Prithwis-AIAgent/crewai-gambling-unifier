#!/usr/bin/env python
"""
Simple RAG Chat Interface for Gambling Unifier
Run this after the main crew has generated the CSV and report files.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from src.gambling_unifier.tools.rag_tool import RAGChatTool

def setup_logging():
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / 'app.log'

    logger = logging.getLogger('gambling_unifier')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

        fh = RotatingFileHandler(log_file, maxBytes=512_000, backupCount=3)
        fh.setLevel(logging.INFO)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger

def load_environment(logger: logging.Logger):
    """Load environment variables from .env file"""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded .env from: {env_path.absolute()}")
    else:
        parent_env = Path('../.env')
        if parent_env.exists():
            load_dotenv(parent_env)
            logger.info(f"Loaded .env from: {parent_env.absolute()}")
        else:
            logger.warning("No .env file found, using system environment variables")

def chat_with_rag():
    """Interactive chat using the RAG system"""

    logger = setup_logging()
    load_environment(logger)

    print("🤖 RAG Chat Interface for Gambling Unifier")
    print("=" * 50)
    print("Ask questions about the unified gambling products!")
    print("Type 'quit' to exit")
    print()

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LITELLM_API_KEY') or os.getenv('LLM_API_KEY')
    if not api_key:
        logger.error("No API key found (OPENAI_API_KEY/LITELLM_API_KEY/LLM_API_KEY)")
        print("❌ Error: No API key found! Set OPENAI_API_KEY or LITELLM_API_KEY or LLM_API_KEY")
        return

    logger.info("API key detected")

    rag_tool = RAGChatTool()

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                logger.info("User exited chat")
                print("Goodbye! 👋")
                break

            if not question:
                continue

            logger.info(f"Received question: {question}")
            print("\n🤖 Searching through your data...")

            result = rag_tool._run(question)
            logger.info("RAG query completed")

            print(f"\n🤖 {result}")
            print("\n" + "-" * 50 + "\n")

        except KeyboardInterrupt:
            logger.info("User interrupted chat with CTRL+C")
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.exception("Unhandled error in chat loop")
            print(f"\n❌ Error: {e}")
            print("Try asking a different question or check if the CSV/report files exist.")

if __name__ == "__main__":
    chat_with_rag()
