import pathlib
from collections import Counter
from os.path import exists
import matplotlib.pyplot as plt

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
OUTPUT_FILENAME = "ioc_results.txt"
OUTPUT_DIAGRAM = "ioc_diagram.png"


def calculate_ioc(text):
    n = len(text)
    if n <= 1:
        return 0.0

    letter_counts = Counter(text)

    summation_term = 0.0
    for char in ALPHABET:
        nt = letter_counts.get(char, 0)
        summation_term += nt * (nt - 1)

    denominator = n * (n - 1)

    ioc = summation_term / denominator
    return ioc


def main():
    files = []

    open_text_file = pathlib.Path("filtered_text.txt")
    if open_text_file.exists():
        files.append(open_text_file)
    else:
        print(f"File {open_text_file} does not exist")

    ciphertext_dir = pathlib.Path("ciphertexts")
    if ciphertext_dir.exists():
        files.extend(list(ciphertext_dir.glob("*.txt")))
    else:
        print(f"Directory {ciphertext_dir} does not exist")

    if not files:
        print("No files found")
        return

    results = []

    print(f"--- Indexes for files ---")
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()

        ioc_value = calculate_ioc(text)
        results.append((file, ioc_value))

    results.sort(key=lambda item: item[1], reverse=True)

    print("Results are sorted")

    header = f"{'File':<25} | {'IoC':<20}"
    separator = "-" * 48

    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            print(header)
            f.write(header + "\n")

            print(separator)
            f.write(separator + "\n")

            for name, ioc in results:
                line = f"{name.name:<25} | {ioc:<20.8f}"
                print(line)
                f.write(line + "\n")

        print(f"Results written to {OUTPUT_FILENAME}")
    except IOError as e:
        print(e)

    print(f"\nCreating diagram '{OUTPUT_DIAGRAM}'...")
    try:
        file_names = [r[0].name for r in results]
        ioc_values = [r[1] for r in results]

        file_names.reverse()
        ioc_values.reverse()

        plt.figure(figsize=(12, 7))

        plt.barh(file_names, ioc_values, color='steelblue')

        plt.xlabel("Індекс відповідності (IoC)")
        plt.ylabel("Файл")
        plt.title("Індекси відповідності для текстів")

        plt.grid(axis='x', linestyle='--', alpha=0.7)

        for index, value in enumerate(ioc_values):
            plt.text(value, index, f" {value:.6f}", va='center')

        plt.tight_layout()

        plt.savefig(OUTPUT_DIAGRAM)
        print(f"Diagram successfully saved to '{OUTPUT_DIAGRAM}'")

    except Exception as e:
        print(f"An error occurred while creating the diagram: {e}")


if __name__ == "__main__":
    main()