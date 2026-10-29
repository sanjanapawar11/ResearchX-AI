import sys
import sqlite3
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import (
    get_research_by_id,
    get_research_history,
    initialize_database,
    save_research,
)
from workflow.graph import run_research


# ==================================================
# 1. Page configuration
# ==================================================

st.set_page_config(
    page_title="ResearchX AI",
    page_icon="🔬",
    layout="wide",
)


initialize_database()


# ==================================================
# 2. Session state
# ==================================================

if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""

if "research_report" not in st.session_state:
    st.session_state.research_report = ""

if "research_id" not in st.session_state:
    st.session_state.research_id = None


# ==================================================
# 3. Helper functions
# ==================================================

def format_timestamp(timestamp: str) -> str:
    """Format an ISO timestamp for display."""

    try:
        return timestamp.replace("T", " ").split(".")[0]
    except (AttributeError, TypeError):
        return timestamp or "Unknown date"


# ==================================================
# 4. Sidebar: Research history
# ==================================================
with st.sidebar:
    st.title("📚 Research History")

    st.caption("Reopen your previous research reports.")

    if st.button("🔄 Refresh History", use_container_width=True):
        st.session_state.pop("history_cache", None)
        st.rerun()

    try:
        if "history_cache" not in st.session_state:
            st.session_state.history_cache = get_research_history()

        history = st.session_state.history_cache

        if not history:
            st.info("No saved research reports yet.")

        else:
            st.caption(f"{len(history)} recent research tasks")

            for item in history:
                research_id = item["id"]
                topic = item["topic"]
                timestamp = format_timestamp(
                    item.get("created_at", "")
                )

                with st.container(border=True):
                    st.markdown(f"**{topic}**")
                    st.caption(f"📅 {timestamp}")

                    if st.button(
                        "Open Report",
                        key=f"open_report_{research_id}",
                        use_container_width=True,
                    ):
                        try:
                            saved_report = get_research_by_id(research_id)
                            if saved_report is None:
                                st.error("Unable to open report: report not found.")
                            else:
                                st.session_state.research_id = (
                                    saved_report["id"]
                                )
                                st.session_state.research_topic = (
                                    saved_report["topic"]
                                )
                                st.session_state.research_report = (
                                    saved_report["report"]
                                )

                                st.rerun()

                        except sqlite3.Error as error:
                            st.error(
                                f"Unable to load the saved report: {error}"
                            )

    except sqlite3.Error as error:
        st.error(f"Cannot load research history: {error}")


# ==================================================
# 5. Main dashboard
# ==================================================

st.title("🔬 ResearchX AI")

st.markdown(
    """
    ### Multi-Agent Research & Intelligence System

    Research smarter. Analyze evidence. Generate structured reports.

    ResearchX AI uses specialized AI stages to plan research,
    retrieve web information, analyze findings, assess claims,
    and generate reports.
    """
)

st.divider()


# ==================================================
# 6. Research input
# ==================================================

st.subheader("📝 Start a New Research Task")

topic = st.text_area(
    "Enter your research topic",
    value="",
    placeholder=(
        "Example: Impact of Generative AI "
        "on the Indian IT industry in 2026"
    ),
    height=120,
    max_chars=500,
)


st.caption(
    "Research reports may take some time to generate "
    "because multiple AI stages and web searches are involved."
)




# ==================================================
# 7. Run the research workflow
# ==================================================

if st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True,
):
    if len(topic.strip()) < 3:
        st.warning("Please enter a topic with at least 3 characters.")

    else:
        try:
            with st.spinner(
                "ResearchX AI is researching and preparing your report..."
            ):
                result = run_research(topic.strip())
                report = result["final_report"]
                research_id = save_research(
                    topic=topic.strip(),
                    report=report,
                )

            st.session_state.research_id = research_id
            st.session_state.research_topic = topic.strip()
            st.session_state.research_report = report

            # Invalidate the cached history after saving a new report.
            st.session_state.pop("history_cache", None)

            st.success("Research report generated and saved!")

            # Reload the page to refresh the sidebar.
            st.rerun()

        except Exception as error:
            st.error(f"Research failed: {error}")


# ==================================================
# 9. Display the selected report
# ==================================================

if st.session_state.research_report:
    st.divider()

    st.subheader("📄 Research Report")

    st.markdown(
        f"**Research topic:** {st.session_state.research_topic}"
    )

    if st.session_state.research_id is not None:
        st.caption(
            f"Report ID: {st.session_state.research_id}"
        )

    report = st.session_state.research_report

    st.markdown(report)

    st.download_button(
        label="📥 Download Research Report",
        data=report,
        file_name="researchx_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

else:
    st.info(
        "Enter a research topic and click Start Research, "
        "or open a previous report from the sidebar."
    )


# ==================================================
# 10. Footer
# ==================================================

st.divider()

st.caption(
    "ResearchX AI | Gemini • LangGraph • MCP • Tavily "
    "• Streamlit • SQLite"
)
