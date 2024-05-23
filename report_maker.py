import re
import requests
import json
from datetime import datetime


class LibraryChecker:

    def __init__(self, input_file, report_folder, choice, report_date=None, search_libs=None):
        self.report_folder = report_folder
        with open(self.report_folder, "w") as f:
            f.write("")
        self.input_file = input_file
        self.url = "https://search.maven.org/solrsearch/select?"
        self.choice = choice
        if report_date:
            self.report_date = datetime.strptime(report_date, "%Y-%m-%d")
        else:
            self.report_date = report_date
        self.search_libs = search_libs

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

    def write_report(self, report):
        with open(self.report_folder, "a") as f:
            f.write(report + "\n")
        return

    def make_report(self, lib_line: str, data: str):
        cur_vers_exist = 0
        late_vers_exist = 0
        lib_line = lib_line.split(":")
        if len(data) > 0:
            latest_version_dict = max(data, key=lambda x: x["timestamp"])
            late_vers_exist = 1

        if self.search_libs:
            self.write_report(
                f'{lib_line[0] + ":" + lib_line[1]}\n\tlatest version: {latest_version_dict["v"]}, datetime: {datetime.fromtimestamp(latest_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}\n'
            )
            return

        current_version_dict = [d for d in data if d["v"] == lib_line[3]]

        if len(current_version_dict) > 0:
            current_version_dict = current_version_dict[0]
            cur_vers_exist = 1

        if self.report_date:
            if cur_vers_exist == 1:
                if datetime.fromtimestamp(current_version_dict["timestamp"] / 1000) < self.report_date:
                    self.write_report(
                        f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}\n'
                    )
                    # data = [d for d in data if datetime.fromtimestamp(d["timestamp"] / 1000) < report_date]
                    return
                else:
                    return
            else:
                return
            return

        if cur_vers_exist == 1:
            if late_vers_exist == 1:
                report = f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")},\n\tlatest version before 2022: {latest_version_dict["v"]}, latest datetime before 2022: {datetime.fromtimestamp(latest_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}'
                self.write_report(report)
                return
            else:
                report = f'{lib_line[0] + ":" + lib_line[1]}\n\tcurrent version: {current_version_dict["v"]}, datetime: {datetime.fromtimestamp(current_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}, \n\tlatest version before 2022 does not exist'
                self.write_report(report)
                return
        else:
            if late_vers_exist == 1:
                self.write_report(
                    f'{":".join(lib_line)}\n\tcurrent version does not exist in repository,\n\tlatest version before 2022: {latest_version_dict["v"]}, latest datetime before 2022: {datetime.fromtimestamp(latest_version_dict["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")}'
                )

                return
            else:
                self.write_report(
                    f"{':'.join(lib_line)}\n\tcurrent version does not exist in repository,\n\tlatest version before 2022 does not exist"
                )
                return

    def get_response(self, params):
        r = requests.get(url=self.url, params=params)
        data = json.loads(r.content)["response"]
        return data["docs"], data["numFound"]

    def run(self):

        try:
            requests.get("http://ya.ru")
        except requests.exceptions.ConnectionError:
            return None

        with open(self.input_file, "r") as f:
            file = f.read()

        # 1- лог, 3 - дата
        if self.choice in ["1", "3"]:
            libs_list = self.get_libs_list(file)
        # 2- модуль
        elif self.choice == "2":
            libs_list = [lib.strip() for lib in self.search_libs.split(",")]

        for lib_line in libs_list:
            data, numFound = self.get_response(self.make_params(lib_line))
            if numFound == 0:
                # with open(self.report_folder, "a") as f:
                #    f.write(f"{lib_line}\n\thas no folder in repository\n")
                continue
            self.make_report(lib_line, data)
        return 1


if __name__ == "__main__":

    checker = LibraryChecker("./input_log.txt", "./report.txt", "2", search_libs="axis:axis-saaj")
    checker.run()
