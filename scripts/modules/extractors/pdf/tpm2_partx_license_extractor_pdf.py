import re
from modules.extractors.license_extractor import LicenseExtractor


class LicenseExtractorPDF(LicenseExtractor):

    # Formats line from license to look like C code comment
    # Parameters:
    # line
    # Returns:
    # same line looking like a C code comment
    def format_line_pdf(self, line):

        result = re.search("^(1|2|3)\.", line)
        if "Licenses and Notices" in line or result:
            formatted_line = self.EMPTY_LINE + self.BEGIN + line
        else:
            formatted_line = self.BEGIN + "   " + line

        return formatted_line + self.indented_end(formatted_line)

    # Extracts the license from any part of the specification by finding its title, and taking the content of that page
    # Parameters:
    # txt_file
    # Returns:
    # string containing license, looking like a C comment block
    def extract_license_pdf(self, txt_file):

        txt_file.seek(0)

        while True:

            line = txt_file.readline()[:-1]
            if "Licenses and Notices" in line:
                break

            if txt_file.tell() == txt_file.size():  # end of file
                raise AssertionError("LICENSE TEXT NOT FOUND")

        self.content += self.format_line_pdf(line.strip())

        while True:
            line = txt_file.readline()[:-1]

            if "CONTENTS" in line:
                break

            if line.strip() == "":
                continue

            if line.startswith("Page") or line.startswith("Family"):
                for i in range(0, 4):
                    line = txt_file.readline()[:-1]
                continue

            self.content += self.format_line_pdf(line.strip())

        self.content += self.EMPTY_LINE
        self.content += self.BORDER_LINE

        return self.content
    # end of method - extract_license_pdf(self, file):
