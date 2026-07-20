import uuid

from workflows.workflow_state import WorkflowState


class WorkflowManager:

    def create_workflow(self, query: str) -> WorkflowState:

        return WorkflowState(workflow_id=str(uuid.uuid4()), query=query)
