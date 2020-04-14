# simple wrappers around pdfrw
import io
import tempfile
from dataclasses import dataclass
from typing import IO, Any, Dict, List, Optional

import pypdftk


@dataclass
class PDFTemplateSection:
    path: str
    is_form: bool = False


class PDFTemplate:
    """
    Constructs a template out a set of input PDFs with fillable AcroForms.
    """

    def __init__(self, template_files: List[PDFTemplateSection]):
        self._template_files = template_files

    def fill(self, raw_data: Dict[str, Any]) -> IO:
        """
        Concatenates all the template_files in this PDFTemplate, and fills in
        the concatenated form with the given data.
        """

        # remove "None" values from data and map True -> "On"
        data = {}
        for k, v in raw_data.items():
            if v is None:
                continue

            if v == True:
                data[k] = "On"
                continue

            data[k] = v

        # Create the final output file and track all the temp files we'll have
        # to close at the end
        final_pdf = tempfile.NamedTemporaryFile("rb+", delete=False)
        handles_to_close: List[IO] = []

        try:
            # Fill in all of the forms
            filled_templates = []
            for template_file in self._template_files:
                if not template_file.is_form:
                    filled_templates.append(template_file.path)
                    continue

                filled_template = tempfile.NamedTemporaryFile("r", delete=False)
                handles_to_close.append(filled_template)
                pypdftk.fill_form(
                    pdf_path=template_file.path,
                    datas=data,
                    out_file=filled_template.name,
                    flatten=False,
                )

                filled_templates.append(filled_template.name)

            # Join the filled forms
            pypdftk.concat(files=filled_templates, out_file=final_pdf.name)

        except:
            final_pdf.close()
            raise
        finally:
            for handle in handles_to_close:
                handle.close()

        return final_pdf
