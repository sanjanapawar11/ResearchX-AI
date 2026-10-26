import os

import requests
import streamlit as st


# ==================================================
# 1. Page configuration
# ==================================================

st.set_page_config(
    page_title="ResearchX AI",
    page_icon="🔬",
    layout="wide",
)


# ==================================================
# 2. API configuration
# ==================================================

API_URL = os.getenv(
    "RESEARCHX_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 600


# ==================================================
# 3. Session state
# ==================================================

if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""

if "research_report" not in st.session_state:
    st.session_state.research_report = ""

if "research_id" not in st.session_state:
    st.session_state.research_id = None


# ==================================================
# 4. Helper functions
# ==================================================

def fetch_history():
    """Retrieve previous research tasks from FastAPI."""

    response = requests.get(
        f"{API_URL}/history",
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def fetch_report(research_id: int):
    """Retrieve a previously saved research report."""

    response = requests.get(
        f"{API_URL}/history/{research_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def format_timestamp(timestamp: str) -> str:
    """Format an ISO timestamp for display."""

    try:
        return timestamp.replace("T", " ").split(".")[0]
    except (AttributeError, TypeError):
        return timestamp or "Unknown date"


# ==================================================
# 5. Sidebar: Research history
# ==================================================

with st.sidebar:
    st.title("📚 Research History")

    st.caption("Reopen your previous research reports.")

    if st.button("🔄 Refresh History", use_container_width=True):
        st.session_state.pop("history_cache", None)
        st.rerun()

    try:
        if "history_cache" not in st.session_state:
            st.session_state.history_cache = fetch_history()

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
                            saved_report = fetch_report(research_id)

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

                        except requests.RequestException as error:
                            st.error(
                                f"Unable to open report: {error}"
                            )

    except requests.RequestException:
        st.warning(
            "Cannot load research history. "
            "Make sure the FastAPI backend is running."
        )


# ==================================================
# 6. Main dashboard
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
# 7. Research input
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
# 8. Run the research workflow
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
                response = requests.post(
                    f"{API_URL}/research",
                    json={"topic": topic.strip()},
                    timeout=REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                data = response.json()

            st.session_state.research_id = data.get("id")
            st.session_state.research_topic = data["topic"]
            st.session_state.research_report = data["report"]

            # Invalidate the cached history after saving a new report.
            st.session_state.pop("history_cache", None)

            st.success("Research report generated and saved!")

            # Reload the page to refresh the sidebar.
            st.rerun()

        except requests.exceptions.Timeout:
            st.error(
                "The research request timed out. "
                "Check the backend terminal before retrying."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the FastAPI backend. "
                "Start the backend and try again."
            )

        except requests.exceptions.HTTPError as error:
            st.error(
                f"The backend returned an HTTP error: {error}"
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Research request failed: {error}")

        except (KeyError, ValueError) as error:
            st.error(f"Unexpected API response: {error}")


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
    "• FastAPI • Streamlit • SQLite"
)

