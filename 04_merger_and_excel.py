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
    apply_city_mapping
)
from tanulmanyi_versenyek.validation.school_matcher import (
    load_kir_database,
    load_school_mapping,
    match_all_schools,
    apply_matches,
    generate_audit_file
)

log = logging.getLogger('04_merger_and_excel')


def validate_kir_file_exists(cfg):
    """Validate KIR file exists before proceeding."""
    kir_file = Path(cfg['kir']['locations_file'])
    if not kir_file.exists():
        raise FileNotFoundError(
            f"KIR database file not found: {kir_file}\n"
            f"Please run: poetry run python 03_download_helper_data.py"
        )


def main():
    """
    Main function for the merger and Excel report generation script.
    Sets up logging and loads configuration.
    """
    logger.setup_logging()
    log.info("Script starting: 04_merger_and_excel.py")
    try:
        cfg = config.get_config()
        log.info("Configuration loaded successfully.")

        validate_kir_file_exists(cfg)
        log.info("KIR file validation passed")

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

        log.info("Applying city corrections...")
        city_mapping = load_city_mapping(cfg)
        master_df, city_corrections = apply_city_mapping(master_df, city_mapping)

        log.info("Loading KIR database...")
        kir_df = load_kir_database(cfg)

        log.info("Loading manual school mappings...")
        school_mapping = load_school_mapping(cfg)

        log.info("Matching schools to KIR database...")
        match_results = match_all_schools(master_df, kir_df, school_mapping, cfg)

        log.info("Applying school matches...")
        original_count = len(master_df)
        master_df = apply_matches(master_df, match_results)
        final_count = len(master_df)
        log.info(f"Records: {original_count} → {final_count} (dropped {original_count - final_count})")

        log.info("Generating audit file...")
        audit_path = Path(cfg['paths']['audit_file'])
        generate_audit_file(match_results, audit_path)

        master_csv_path = Path(cfg['paths']['master_csv'])
        master_df.to_csv(master_csv_path, sep=';', encoding='utf-8', index=False)
        log.info(f"Master CSV saved to {master_csv_path}")

        generate_validation_report(master_df, cfg, duplicates_removed, city_corrections, match_results)
        generate_excel_report(master_df, cfg)

        log.info("Script completed successfully")
    except FileNotFoundError as e:
        log.error(str(e))
        raise
    except Exception as e:
        log.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
