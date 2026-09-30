import logging


from app.reports.pdf_reports import PDF_REPORT_PATH, generate_event_dashboard_pdf
from app.api.schemas.event import EventDashboard
from app.infrastructure.taskiq.brokers import cpu_broker

logger = logging.getLogger(__name__)


@cpu_broker.task(
    task_name="generate_event_dashboard_report",
    max_retries=3,
    retry_on_error=True,
)
async def generate_event_dashboard_report(event_id: int, event_dashboard: EventDashboard) -> None:
    logger.info("Report formation started")
    generate_event_dashboard_pdf(
        event_id=event_id,
        dashboard=event_dashboard,
        output_path=PDF_REPORT_PATH,
    )
    logger.info("Report formation finished")
