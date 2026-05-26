"""CLI entry point for the DayZ AI Puppet controller."""

from __future__ import annotations

import argparse
import logging
import signal
import sys

from dayz_ai_puppet.config import Settings
from dayz_ai_puppet.loop import DayZAILoop


def main() -> None:
    parser = argparse.ArgumentParser(description="DayZ AI Puppet — embodied survival AI")
    parser.add_argument("--config", default=".env", help="Path to .env config file")
    parser.add_argument(
        "--tick-rate", type=float, default=None,
        help="Seconds between decision cycles",
    )
    parser.add_argument(
        "--log-level", default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    parser.add_argument(
        "--no-reflexes", action="store_true",
        help="Disable hardcoded reflex layer",
    )
    parser.add_argument(
        "--monitor", type=int, default=None,
        help="Monitor index for screen capture (1=primary)",
    )
    args = parser.parse_args()

    settings = Settings(_env_file=args.config)

    if args.tick_rate is not None:
        settings.tick_rate = args.tick_rate
    if args.log_level is not None:
        settings.log_level = args.log_level
    if args.no_reflexes:
        settings.reflex_enabled = False
    if args.monitor is not None:
        settings.capture_monitor = args.monitor

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    loop = DayZAILoop(settings)

    def _signal_handler(sig, frame):
        logging.getLogger(__name__).info("received signal %s, shutting down", sig)
        loop.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    loop.run()


if __name__ == "__main__":
    main()
