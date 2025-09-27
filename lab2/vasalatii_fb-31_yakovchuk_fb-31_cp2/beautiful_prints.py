from colorama import Fore, Style
import pandas as pd
from tabulate import tabulate

def print_error(error: str) -> None:
	print(Fore.RED + error + Style.RESET_ALL)

def print_green_blue_colored_pair(tag: str, value: str | int | float | dict, indentation: str='') -> None:
	print(indentation + Fore.LIGHTGREEN_EX + tag + " " + Fore.LIGHTBLUE_EX + str(value) + Style.RESET_ALL)

def print_df(frame: pd.DataFrame, title: str=None) -> None:
	table_str = tabulate(frame, headers='keys', tablefmt="heavy_grid", showindex=False)
	table_width = max(len(line) for line in table_str.splitlines())

	if title:
		print(Fore.LIGHTGREEN_EX + title.center(table_width) + Style.RESET_ALL)

	print(Fore.LIGHTCYAN_EX + table_str + Style.RESET_ALL)