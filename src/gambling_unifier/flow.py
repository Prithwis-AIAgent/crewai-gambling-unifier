from crewai import Crew, Process
from gambling_unifier.crew import GamblingUnifier


def build_flow() -> Crew:
    crew = GamblingUnifier().crew()
    # Sequential process already set in GamblingUnifier. Could be adjusted here if needed.
    crew.process = Process.sequential
    return crew


