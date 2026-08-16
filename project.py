def main():
    # 1. check command line argument
    # 2. check if file exists and can be opened
    # 3. check for expected header format
    # setup: seen = set(), valid = [], errors = []
    # 4. loop to read and process data
        # 4a. try to normalize name, email and phone
        # 4b. if normalization fails -> add to errors list with reason
        # 4c. if email already seen -> add to errors list as duplicate
        # 4d. otherwise -> add email to seen, add contact to valid list
    # 5. write output files (clean and rejected)
    # 6. summary on terminal
    ...


def normalize_name(name):
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("empty name")
    return clean_name.title()