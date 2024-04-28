from report_maker import LibraryChecker

# from gui import LibraryCheckerGUI

if __name__ == "__main__":
    checker = LibraryChecker("./input_log.txt", "./report.txt", "3", "2006-01-01")
    checker.run()
