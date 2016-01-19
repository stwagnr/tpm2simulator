from modules.extractors.license_extractor import LicenseExtractor
from modules import constants


class LicenseExtractorFODT(LicenseExtractor):
    paragraph_nr = 1

    # Formats paragraph from license to look like C code comment
    # Parameters:
    # text_p
    # Returns:
    # same paragraph looking like a C code comment block
    def format_text_p_fodt(self, text_p):
        text = text_p.get_text().strip()
        formatted_text = ""

        if "Licenses and Notices" in text:
            formatted_text = self.EMPTY_LINE + self.BEGIN + text
            formatted_text += self.indented_end(formatted_text)

        elif text_p.has_attr(constants.XML_TEXT_STYLE_NAME) and "P10" in text_p[constants.XML_TEXT_STYLE_NAME]:
            formatted_text = self.EMPTY_LINE + self.BEGIN + str(self.paragraph_nr) + ".  " + text
            formatted_text += self.indented_end(formatted_text)
            self.paragraph_nr += 1

        else:  # in this case the text might be longer than a normal line
            while len(text) > self.LENGTH - 5:
                idx = text[:self.LENGTH - 5].rfind(" ")
                line = text[:idx]
                formatted_line = self.BEGIN + "   " + line.strip()
                formatted_text += formatted_line + self.indented_end(formatted_line)
                text = text[idx:]

            formatted_line = self.BEGIN + "   " + text.strip()
            formatted_text += formatted_line + self.indented_end(formatted_line)

        return formatted_text

    # Extracts the license from any part of the specification
    # Parameters:
    # xml_file
    # Returns:
    # string containing license, looking like a C comment block
    def extract_license_fodt(self, xml_file):

        all_text_ps = xml_file.find_all(constants.XML_TEXT_P)
        text_p = None

        for one_text_p in all_text_ps:

            if "Licenses and Notices" in one_text_p.get_text():
                text_p = one_text_p
                break

        if not text_p:  # nothing found
            raise AssertionError("LICENSE TEXT NOT FOUND")

        self.content += self.format_text_p_fodt(text_p)

        while True:
            text_p = text_p.find_next(constants.XML_TEXT_P)

            if "CONTENTS" in text_p.get_text():
                break

            self.content += self.format_text_p_fodt(text_p)

        self.content += self.EMPTY_LINE
        self.content += self.BORDER_LINE

        return self.content
        # end of method - extract_license_pdf(self, file):
