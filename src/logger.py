import logging
import streamlit as st
import datetime
import os


def setup_log():
    if "logger_obj" not in st.session_state:
        st.session_state["logger_obj"] = logging.getLogger(__name__)
        now = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        path = f"logs/{now}"
        num = 1

        def make_path(base, n):
            if n == 1:
                return f"{path}.log"
            return f"{path}-({n}).log"
        while os.path.exists(make_path(path, num)):
            num+=1
        path = make_path(path, num)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        st.session_state["logger_filename"] = path

    logging.basicConfig(
        filename=st.session_state["logger_filename"],
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )



def log(*message, level="info"):
    message = " ".join([str(m) for m in message])
    setup_log()
    match level:
        case "info": logging.info(message)
        case "warning": logging.warning(message)
        case "error": logging.error(message)
        case "critical": logging.critical(message)
        case "exception": logging.exception(message)
        case _: logging.info(message)
