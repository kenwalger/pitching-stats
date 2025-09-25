import argparse
from datetime import date, timedelta
from data_processing import process_data, display_data

def main():
    parser = argparse.ArgumentParser(description="Fetch and display pitcher data.")
    parser.add_argument(
        "--start_date",
        help="Start date in YYYY-MM-DD format.",
        default=(date.today() - timedelta(days=5)).strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "--end_date",
        help="End date in YYYY-MM-DD format.",
        default=date.today().strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Number of top/bottom pitchers to display."
    )

    args = parser.parse_args()

    top_pitchers, bottom_pitchers, all_pitchers_summary, general_stats = process_data(args.start_date, args.end_date, args.n)
    display_data(top_pitchers, "TOP", all_pitchers_summary, general_stats)
    display_data(bottom_pitchers, "BOTTOM", all_pitchers_summary, general_stats)


if __name__ == "__main__":
    main()
