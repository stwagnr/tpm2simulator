import settings


class LicenseExtractor:

    LENGTH = 112

    EMPTY_LINE = "/*" + LENGTH * " " + "*/\n"
    BORDER_LINE = "/*" + LENGTH * "*" + "*/\n"
    BEGIN = "/*  "
    END = "*/\n"

    def __init__(self):
        self.content = self.BORDER_LINE
        self.content += self.EMPTY_LINE

    # Indent the ending of the line
    # Parameters:
    # line
    # Returns
    # same line with indented ending
    def indented_end(self, line):
        length = len(line)
        while length > self.LENGTH + 2:
            length -= self.LENGTH + 5

        return (self.LENGTH + 2 - length) * " " + self.END

    # Extracts license from any part of the specification in either text or xml format
    # Parameters:
    # file - file descriptor
    # Returns:
    # string containing license formatted as comment block
    @staticmethod
    def extract_license(file):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_partx_license_extractor_pdf import LicenseExtractorPDF

            license_extractor = LicenseExtractorPDF()
            return license_extractor.extract_license_pdf(file)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_partx_license_extractor_fodt import LicenseExtractorFODT

            license_extractor = LicenseExtractorFODT()
            return license_extractor.extract_license_fodt(file)
