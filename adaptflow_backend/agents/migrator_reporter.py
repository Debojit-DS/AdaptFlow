from graph.state import AdaptFlowState
from models.schemas import MigrationReport
from agents.llm_helper import invoke_structured_llm_with_retry


def run(state: AdaptFlowState) -> AdaptFlowState:
    state["migration_report"] = invoke_structured_llm_with_retry(
        "migrator_reporter",
        MigrationReport,
        f"Create a migration report for: {state.get('workflow_description', '')}",
        retries=2,
    )
    state["status"] = "complete"
    return state
