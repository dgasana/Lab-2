import csv
import math
import os
import sys

def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ")

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    assignments = []

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric fields to floats for calculations
                assignments.append({
                    'assignment': row['assignment'],
                    'group': row['group'],
                    'score': float(row['score']),
                    'weight': float(row['weight'])
                })
        return assignments
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)


def evaluate_grades(data):
    """
    Validates the grades and weights, then prints the GPA, the final
    PASSED / FAILED status and the formative assignment(s) to resubmit.
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    if not data:
        print("Error: the file contains no assignments.")
        sys.exit(1)

    # a) Grade validation: every score must be a percentage (0-100).
    invalid = [a for a in data if not 0 <= a['score'] <= 100]
    if invalid:
        for a in invalid:
            print(f"Error: '{a['assignment']}' has score {a['score']:g}, "
                  "which is outside the 0-100 range.")
        sys.exit(1)

    # Every assignment must belong to a known category.
    for a in data:
        a['category'] = a['group'].strip().capitalize()
        if a['category'] not in ('Formative', 'Summative'):
            print(f"Error: '{a['assignment']}' has unknown group "
                  f"'{a['group']}' (expected Formative or Summative).")
            sys.exit(1)

    # b) Weight validation: Total = 100, Summative = 40, Formative = 60.
    formative = [a for a in data if a['category'] == 'Formative']
    summative = [a for a in data if a['category'] == 'Summative']
    total_weight = sum(a['weight'] for a in data)
    formative_weight = sum(a['weight'] for a in formative)
    summative_weight = sum(a['weight'] for a in summative)

    weight_errors = []
    if not math.isclose(total_weight, 100, abs_tol=1e-9):
        weight_errors.append(
            f"Total weight is {total_weight:g}, expected 100.")
    if not math.isclose(summative_weight, 40, abs_tol=1e-9):
        weight_errors.append(
            f"Summative weight is {summative_weight:g}, expected 40.")
    if not math.isclose(formative_weight, 60, abs_tol=1e-9):
        weight_errors.append(
            f"Formative weight is {formative_weight:g}, expected 60.")
    if weight_errors:
        for message in weight_errors:
            print("Error: " + message)
        sys.exit(1)

    # c) Final grade and GPA.
    formative_points = sum(a['score'] * a['weight'] / 100 for a in formative)
    summative_points = sum(a['score'] * a['weight'] / 100 for a in summative)
    total_grade = formative_points + summative_points
    gpa = (total_grade / 100) * 5.0

    # d) Pass/Fail: at least 50% in BOTH categories.
    formative_pct = formative_points / formative_weight * 100
    summative_pct = summative_points / summative_weight * 100
    passed = formative_pct >= 50 and summative_pct >= 50

    print(f"\n{'Assignment':<40}{'Group':<12}{'Score':>7}{'Weight':>8}")
    for a in data:
        print(f"{a['assignment']:<40}{a['category']:<12}"
              f"{a['score']:>7g}{a['weight']:>8g}")

    print(f"\nFormative: {formative_points:.2f} / {formative_weight:g} "
          f"({formative_pct:.2f}%)")
    print(f"Summative: {summative_points:.2f} / {summative_weight:g} "
          f"({summative_pct:.2f}%)")
    print(f"\nTotal Grade: {total_grade:.2f} / 100")
    print(f"GPA: {gpa:.2f}")
    print(f"Final Status: {'PASSED' if passed else 'FAILED'}")

    # e) Failed formative assignments (< 50%): the one(s) with the highest
    #    weight are eligible for resubmission (all of them on a tie).
    failed = [a for a in formative if a['score'] < 50]
    print("\n--- Resubmission ---")
    if not failed:
        print("No failed formative assignments. No resubmission needed.")
    else:
        highest = max(a['weight'] for a in failed)
        eligible = [a for a in failed if a['weight'] == highest]
        print("Eligible for resubmission (highest weight among failed "
              f"formative assignments, weight {highest:g}):")
        for a in eligible:
            print(f"  - {a['assignment']} (score {a['score']:g}%)")


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
