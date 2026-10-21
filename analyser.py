
import re

SKILLS_LIST = [
    "python", "java", "c++", "javascript", "html", "css",
    "sql", "mysql", "postgresql", "mongodb", "react",
    "node.js", "flask", "django", "streamlit",
    "machine learning", "data analysis", "excel",
    "power bi", "communication", "problem solving",
    "git", "github", "rest api", "typescript",
    "angular", "vue.js", "express.js", "php",
    "c#", ".net", "aws", "azure", "docker",
    "kubernetes", "linux", "cybersecurity",
    "data structures", "algorithms", "teamwork",
    "leadership", "project management", "testing"
]


def extract_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def analyse_job(job_description, user_skills):
    required_skills = extract_skills(job_description)
    existing_skills = extract_skills(user_skills)

    matched_skills = [
        skill for skill in required_skills
        if skill in existing_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in existing_skills
    ]

    match_percentage = 0

    if required_skills:
        match_percentage = round(
            len(matched_skills) / len(required_skills) * 100
        )

    return {
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage
    }


def get_skill_priorities(text, skills):
    text_lower = text.lower()

    high_words = [
        "must have", "mandatory", "essential",
        "required skills", "required qualification",
        "proficient in", "minimum requirement"
    ]

    medium_words = [
        "preferred", "good to have",
        "desirable", "an advantage",
        "preferred qualification"
    ]

    priorities = {
        "High Priority": [],
        "Medium Priority": [],
        "Additional Skills": []
    }

    for skill in skills:
        # Look for the skill in its surrounding sentence.
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        match = re.search(pattern, text_lower)

        if not match:
            priorities["Additional Skills"].append(skill)
            continue

        start = max(0, text_lower.rfind(
            ".", 0, match.start()
        ) + 1)

        end = text_lower.find(".", match.end())

        if end == -1:
            end = len(text_lower)

        sentence = text_lower[start:end]

        if any(word in sentence for word in high_words):
            priorities["High Priority"].append(skill)
        elif any(word in sentence for word in medium_words):
            priorities["Medium Priority"].append(skill)
        else:
            priorities["Additional Skills"].append(skill)

    return priorities


def extract_salary(text):
    patterns = [
        r"(?i)(?:salary|ctc|compensation|package)"
        r"\s*(?:range)?\s*[:\-]?\s*"
        r"(?:INR|Rs\.?|₹)?\s*"
        r"\d[\d,]*(?:\.\d+)?\s*"
        r"(?:-|to)\s*(?:INR|Rs\.?|₹)?\s*"
        r"\d[\d,]*(?:\.\d+)?\s*"
        r"(?:LPA|L\.P\.A\.|lakhs? per annum|"
        r"per annum|annually)?",

        r"(?i)(?:salary|ctc|compensation|package)"
        r"\s*[:\-]?\s*(?:INR|Rs\.?|₹)\s*"
        r"\d[\d,]*(?:\.\d+)?\s*"
        r"(?:LPA|L\.P\.A\.|lakhs? per annum|"
        r"per annum|annually)?"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0).strip()

    return "Not specified in the job description"


def extract_job_title(text):
    lines = [line.strip() for line in text.splitlines()
             if line.strip()]

    # Use a labelled job title when one is provided.
    match = re.search(
        r"(?im)^(?:job title|position|role)\s*:\s*(.+)$",
        text
    )

    if match:
        return match.group(1).strip()

    # Otherwise, the first line is only a possible title.
    if lines:
        return lines[0][:100] + (
            " (possible title; please verify)"
            if len(lines[0]) > 0 else ""
        )

    return "Not specified"


def extract_experience(text):
    patterns = [
        r"(?i)\b\d+\s*(?:-|to)\s*\d+\s*"
        r"(?:years?|yrs?)\s+(?:of\s+)?experience\b",
        r"(?i)\b\d+\+?\s*(?:years?|yrs?)\s+"
        r"(?:of\s+)?experience\b",
        r"(?i)\b(?:fresher|freshers|entry.level|"
        r"no experience required)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return "Not specified"


def extract_labelled_info(text, labels):
    results = []

    for line in text.splitlines():
        for label in labels:
            pattern = (
                r"(?i)^\s*" + re.escape(label)
                + r"\s*:\s*(.+)$"
            )

            match = re.search(pattern, line)

            if match:
                results.append(
                    label.title() + ": " + match.group(1).strip()
                )
                break

    return results


def extract_responsibilities(text):
    responsibilities = []
    keywords = [
        "responsible for", "responsibilities",
        "duties include", "you will",
        "develop", "design", "build", "maintain",
        "manage", "implement", "analyse", "analyze",
        "test", "monitor", "collaborate",
        "coordinate", "support", "create",
        "perform", "lead", "deploy", "troubleshoot"
    ]

    # First check bullet points and numbered list items.
    for line in text.splitlines():
        cleaned = re.sub(r"^\s*[-*•\d.)]+\s*", "", line).strip()

        if len(cleaned) > 15 and any(
            word in cleaned.lower() for word in keywords
        ):
            responsibilities.append(cleaned)

    # If there are no useful list items, inspect sentences.
    if not responsibilities:
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:
            if (
                len(sentence.strip()) > 20
                and any(word in sentence.lower()
                        for word in keywords)
            ):
                responsibilities.append(sentence.strip())

    # Remove duplicate items and limit the output.
    return list(dict.fromkeys(responsibilities))[:10]


def analyse_job_details(text):
    skills = extract_skills(text)
    priorities = get_skill_priorities(text, skills)

    additional_info = extract_labelled_info(
        text,
        [
            "Location", "Work Mode", "Employment Type",
            "Education", "Qualification", "Department",
            "Benefits", "Deadline", "Job Type",
            "Certifications", "Notice Period"
        ]
    )

    return {
        "job_title": extract_job_title(text),
        "experience": extract_experience(text),
        "salary": extract_salary(text),
        "required_skills": skills,
        "priorities": priorities,
        "responsibilities": extract_responsibilities(text),
        "additional_info": additional_info
    }
