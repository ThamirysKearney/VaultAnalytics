def extract_course_info(df):
    def parse_course(code):
        parts = code.split("_")
        return {
            "course_code": parts[3],
            "course_id": parts[4],
            "course_date": parts[5]
        }

    parsed = df["course_edition"].apply(parse_course)
    df["course_code"] = parsed.apply(lambda x: x["course_code"])
    df["course_id"] = parsed.apply(lambda x: x["course_id"])
    df["course_date"] = parsed.apply(lambda x: x["course_date"])

    return df


def create_age_groups(df):
    bins = [0, 25, 35, 45, 100]
    labels = ["18-25", "26-35", "36-45", "46+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels)
    return df