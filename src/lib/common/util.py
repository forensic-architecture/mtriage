def save_logs(logs, filepath):
    if len(logs) <= 0:
        return
    with open(filepath, "a") as f:
        for l in logs:
            if l is not None:
                f.write(l)
                f.write("\n")
