import re
import requests
import json
from datetime import datetime
from tqdm import *


class LibraryChecker:
    def __init__(self, input_file, report_folder, choice, add=None):
        self.input_file = input_file
        self.report_folder = report_folder
        self.url = "https://search.maven.org/solrsearch/select?"
        self.choice = choice
        self.add = add

    def get_libs_list(self, text: str):
        text = text.splitlines()
        lines = [l for l in text if l.endswith(("compile", "test", "runtime", "provided"))]
        libs_list = set()
        [
            libs_list.add(
                re.search(
                    r"([a-zA-Z0-9\.\-]+:[a-zA-Z0-9\.\-]+:[a-zA-Z0-9\.\-]+:[a-zA-Z0-9\.\-]+)",
                    s,
                ).group()
            )
            for s in lines
        ]
        libs_list = list(libs_list)
        libs_list.sort()
        return libs_list

    def make_params(self, lib_line: str):
        q_pattern = "g:{} AND a:{}"
        lib_param = lib_line.split(":")
        params = {
            "core": "gav",
            "q": q_pattern.format(lib_param[0], lib_param[1]),
            "version": "2.2",
        }
        return params

    def make_report(self, lib_line: str, data: str, numFound: int, report_date: str = None):
        cur_vers_exist = 0
        late_vers_exist = 0
        if numFound == 0:
            with open(self.report_folder, "a") as f:
                f.write(f"{lib_line}\n\thas no folder in repository\n")
            return
        lib_line = lib_line.split(":")
        current_version_dict = [d for d in data if d["v"] == lib_line[3]]

        if len(current_version_dict) > 0:
            current_version_dict = current_version_dict[0]
            cur_vers_exist = 1

        if len(data) > 0:
            latest_version_dict = max(data, key=lambda x: x["timestamp"])
            late_vers_exist = 1

        if report_date:
            if cur_vers_exist == 1:
                report_date = datetime.strptime(report_date, "%Y-%m-%d")
                if datetime.fromtimestamp(current_version_dict["timestamp"] / 1000) < report_date:

                    # data = [d for d in data if datetime.fromtimestamp(d["timestamp"] / 1000) < report_date]
                    with open(self.report_folder, "a") as f:
                        f.write(
                            f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}\n'
                        )
                        return
                else:
                    return
            else:
                return

        if cur_vers_exist == 1:

            if late_vers_exist == 1:
                report = f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")},\n\tlatest version before {report_date.strftime("%Y-%m-%d")}: {latest_version_dict["v"]}, latest datetime before {report_date.strftime("%Y-%m-%d")}: {datetime.fromtimestamp(latest_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}'
                with open(self.report_folder, "a") as f:
                    f.write(report + "\n")
                return
            else:
                report = f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")},\n\tlatest version before {report_date.strftime("%Y-%m-%d")} does not exist'
                with open(self.report_folder, "a") as f:
                    f.write(report + "\n")
                return
        else:
            if late_vers_exist == 1:
                with open(self.report_folder, "a") as f:
                    f.write(
                        f'{":".join(lib_line)}\n\tcurrent version does not exist in repository,\n\tlatest version before {report_date.strftime("%Y-%m-%d")}: {latest_version_dict["v"]}, latest datetime before {report_date.strftime("%Y-%m-%d")}: {datetime.fromtimestamp(latest_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}'
                        + "\n"
                    )
                return
            else:
                with open(self.report_folder, "a") as f:
                    f.write(
                        f"{':'.join(lib_line)}\n\tcurrent version does not exist in repository,\n\tlatest version before {report_date.strftime('%Y-%m-%d')} does not exist"
                        + "\n"
                    )
                return

    def get_response(self, params):
        r = requests.get(url=self.url, params=params)
        data = json.loads(r.content)["response"]
        return data["docs"], data["numFound"]

    def run(self):
        with open(self.input_file, "r") as f:
            file = f.read()

        if self.choice == "1":
            libs_list = self.get_libs_list(file)
            for lib_line in tqdm(libs_list):
                data, numFound = self.get_response(self.make_params(lib_line))
                self.make_report(lib_line, data, numFound)
        elif self.choice == "2":
            libs_list = [lib.strip() for lib in self.add.split(",")]
            for lib_line in tqdm(libs_list):
                data, numFound = self.get_response(self.make_params(lib_line))
                self.make_report(lib_line, data, numFound)
        elif self.choice == "3":
            libs_list = self.get_libs_list(file)
            for lib_line in tqdm(libs_list):
                data, numFound = self.get_response(self.make_params(lib_line))
                self.make_report(lib_line, data, numFound, self.add)
        else:
            print("Invalid choice. Exiting.")


if __name__ == "__main__":

    checker = LibraryChecker("./input_log.txt", "./report.txt", "2")
    checker.run()
