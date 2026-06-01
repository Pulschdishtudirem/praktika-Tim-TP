import sys
import pandas as pd

df = None

DATASET_URL = "https://raw.githubusercontent.com/Pulschdishtudirem/praktika-Tim-TP/refs/heads/main/dataset.csv"

def load_data():
    """Загружает данные из репозитория Git в глобальную переменную df."""
    global df
    try:
        print("Загрузка данных из Git репозитория...")
        df = pd.read_csv(DATASET_URL, index_col=0)
        print("Данные успешно загружены.\n")
    except Exception as e:
        print(f"Ошибка при загрузке файла из Git: {e}")
        print("Проверьте интернет-соединение и доступность ссылки.")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

def generate_report():
    """Анализирует данные и выводит отчет в консоль и файл report.txt."""
    if df is None:
        return

    report_lines = []

    rows, cols = df.shape
    report_lines.append("--- Отчет о наборе данных ---\n")
    report_lines.append(f"Количество строк: {rows}")
    report_lines.append(f"Количество колонок: {cols}\n")

    report_lines.append("--- Типы данных по колонкам ---")
    report_lines.append(df.dtypes.to_string())
    report_lines.append("")

    report_lines.append("--- Количество незаполненных ячеек (NaN) ---")
    null_counts = df.isnull().sum()
    report_lines.append(null_counts.to_string())
    report_lines.append("")

    report_lines.append("--- Базовая статистика (числовые колонки) ---")
    numerical_stats = df.describe().transpose()
    if not numerical_stats.empty and "mean" in numerical_stats.columns:
        report_lines.append(numerical_stats[["mean", "50%", "std"]].to_string())
    else:
        report_lines.append("Числовые колонки отсутствуют.")
    report_lines.append("")

    report_lines.append(
        "--- Категориальные признаки (уникальные значения) ---"
    )
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    for col in categorical_cols:
        report_lines.append(f"Колонка '{col}':")
        counts = df[col].value_counts()
        report_lines.append(counts.to_string())
        report_lines.append("")

    full_report = "\n".join(report_lines)

    print(full_report)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(full_report)


if __name__ == "__main__":
    load_data()
    generate_report()

    input("\nРасчет завершен. Нажмите Enter для выхода...")
