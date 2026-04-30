import sys
from loguru import logger
from pathlib import Path
import os

def configure_logging():
    logger.remove()

    current_file_path = Path(__file__).resolve().parent
    log_dir = current_file_path.parent / "logs"

    log_dir.mkdir(exist_ok=True)


    logger.add(
            sys.stderr,
            format="<green>{time:YYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name} (line: {line}) :{function}</cyan> - {message}",
            level='INFO',
            backtrace=True,
            diagnose=True
            )
    log_file_path = log_dir / "beam_sim_{time}.log"
    logger.add(
            str(log_file_path),
            rotation="1 day",
            level='DEBUG',
            compression='zip'
            )
def main():
    configure_logging()
    logger.info("Starting Optical Layout somulation")

    pass



if __name__ == "__main__":
    main()

