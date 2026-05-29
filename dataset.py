import pandas as pd
import sys

df = None


def load_data():
    """Загружает данные из dataset.csv в глобальную переменную df."""
    global df
    try:
        df = pd.read_csv(r'dataset.csv', index_col=0)
    except FileNotFoundError:
        print("Ошибка: Файл 'dataset.csv' не найден.")
        input("\nНажмите Enter для выхода...")  # Держит окно при ошибке
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        input("\nНажмите Enter для выхода...")  # Держит окно при ошибке
        sys.exit(1)


def generate_report():
    """Анализирует данные и выводит отчет в консоль и файл report.txt."""
    if df is None:
        return

    report_lines = []

    rows, cols = df.shape
    report_lines.append(f"--- Отчет о наборе данных ---\n")
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
    report_lines.append(numerical_stats[['mean', '50%', 'std']].to_string())
    report_lines.append("")

    report_lines.append("--- Категориальные признаки (уникальные значения) ---")
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    for col in categorical_cols:
        report_lines.append(f"Колонка '{col}':")
        counts = df[col].value_counts()
        report_lines.append(counts.to_string())
        report_lines.append("")

    full_report = "\n".join(report_lines)

    print(full_report)

    with open('report.txt', 'w', encoding='utf-8') as f:
        f.write(full_report)


if __name__ == "__main__":
    load_data()
    generate_report()

    input("\nРасчет завершен. Нажмите Enter для выхода...")