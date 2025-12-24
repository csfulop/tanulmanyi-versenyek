import logging
import shutil
from pathlib import Path
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger
from tanulmanyi_versenyek.merger.data_merger import (
    merge_processed_data,
    generate_validation_report,
    generate_excel_report
)
from tanulmanyi_versenyek.validation.city_checker import (
    load_city_mapping,
    apply_city_mapping,
    check_city_variations
)

log = logging.getLogger('03_merger_and_excel')


def main():
    """
    Main function for the merger and Excel report generation script.
    Sets up logging and loads configuration.
    """
    logger.setup_logging()
    log.info("Script starting: 03_merger_and_excel.py")
    try:
        cfg = config.get_config()
        log.info("Configuration loaded successfully.")

        kaggle_template_dir = Path(cfg['paths']['kaggle_template_dir'])
        kaggle_output_dir = Path(cfg['paths']['kaggle_dir'])

        if kaggle_output_dir.exists():
            shutil.rmtree(kaggle_output_dir)
            log.info(f"Cleaned up existing Kaggle directory: {kaggle_output_dir}")

        kaggle_output_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Created Kaggle directory: {kaggle_output_dir}")

        if kaggle_template_dir.exists():
            for item in kaggle_template_dir.iterdir():
                if item.is_file():
                    shutil.copy(item, kaggle_output_dir / item.name)
                    log.info(f"Copied {item.name} to Kaggle directory")
        else:
            log.warning(f"Kaggle template directory not found: {kaggle_template_dir}")

        master_df, duplicates_removed = merge_processed_data(cfg)
        if master_df.empty:
            log.error("Master DataFrame is empty, cannot proceed")
            return

        city_mapping = load_city_mapping(cfg)
        master_df, corrections_applied = apply_city_mapping(master_df, city_mapping)

        master_csv_path = Path(cfg['paths']['master_csv'])
        master_df.to_csv(master_csv_path, sep=';', encoding='utf-8', index=False)
        log.info(f"Master CSV with corrections saved to {master_csv_path}")

        variation_stats = check_city_variations(master_df, city_mapping)

        city_stats = {**variation_stats, 'corrections_applied': corrections_applied}

        generate_validation_report(master_df, cfg, duplicates_removed, city_stats)
        generate_excel_report(master_df, cfg)

        log.info("Script completed successfully")
    except Exception as e:
        log.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
