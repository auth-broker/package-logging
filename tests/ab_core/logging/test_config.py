"""Tests for template entrypoint."""


def test_logging_config():
    """Test a function in the entrypoint is callable."""
    from ab_core.logging.config import LoggingConfig

    config = LoggingConfig()
    config.apply()

    import logging

    logger = logging.getLogger("ab_service.blah")
    logger.debug("Test DEBUG log from test case! (this shouldn't show)")
    logger.info("Test INFO log from test case! (this should show)")
    logger.warning("Test WARNING log from test case! (this should show)")
    logger.error("Test ERROR log from test case! (this should show)")
    try:
        raise Exception("Mock Exception")
    except Exception:
        logger.exception("Test EXCEPTION log from test case! (this should show)")
    logger.critical("Test CRITICAL log from test case! (this should show)")
