import configparser
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF

import click


class InvoiceGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self, inv_date, inv_num):
        inv_date = inv_date.strftime("%d-%b-%Y")
        inv_num = (
            f"{str(inv_num).zfill(int(self.config.get('invoice_num_length', 4)))}"
            f"{self.config.get('invoice_num_suffix', '')}"
        )
        click.echo(f"Generating invoice {inv_num} ({inv_date})")

        # Create document
        pdf = Document()

        # Add page
        page = Page()
        pdf.add_page(page)

        page_layout = SingleColumnLayout(page)
        page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

        page_layout.add(
            Paragraph(
                "INVOICE",
                horizontal_alignment=Alignment.RIGHT,
                font_size=Decimal(16),
                font_color=HexColor("a19f9a"),
            )
        )

        # Invoice information table
        page_layout.add(self._build_invoice_information(inv_date, inv_num))

        # Empty paragraph for spacing
        page_layout.add(Paragraph(" "))

        page_layout.add(self._build_billing_and_shipping_information())

        # Empty paragraph for spacing
        page_layout.add(Paragraph(" "))

        page_layout.add(self._build_itemized_description_table())

        # Empty paragraph for spacing
        page_layout.add(Paragraph(" "))
        page_layout.add(Paragraph(" "))
        page_layout.add(self._build_payment_information())

        output_dir = self.config.get("output_dir", Path(__file__).parent)
        filename = (
            Path(output_dir)
            / f"{self.config['invoice_filename_prefix']}_{inv_num}_{inv_date}.pdf"
        )
        with open(filename, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)
        click.echo(f"Invoice written to {filename}")

    def _build_invoice_information(self, inv_date, inv_num):
        has_company = self.config.get("from_company")
        table_001 = Table(number_of_rows=6 if has_company else 5, number_of_columns=4)

        table_001.add(Paragraph(self.config["from_name"], font="Helvetica-Bold"))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph(" "))

        if has_company:
            table_001.add(Paragraph(self.config["from_company"]))
            table_001.add(Paragraph(" "))
            table_001.add(Paragraph(""))
            table_001.add(Paragraph(""))

        table_001.add(Paragraph(self.config["from_address"]))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph("Date:", font="Helvetica-Bold"))
        table_001.add(Paragraph(inv_date, horizontal_alignment=Alignment.RIGHT))

        table_001.add(Paragraph(self.config["from_city"]))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph("Invoice #:", font="Helvetica-Bold"))
        table_001.add(Paragraph(inv_num, horizontal_alignment=Alignment.RIGHT))

        table_001.add(Paragraph(self.config["from_postcode"]))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph("For:", font="Helvetica-Bold"))
        table_001.add(
            Paragraph(self.config["bill_for"], horizontal_alignment=Alignment.RIGHT)
        )

        table_001.add(Paragraph(self.config["from_email"]))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph(" "))
        table_001.add(Paragraph(" "))

        table_001.set_padding_on_all_cells(
            Decimal(2), Decimal(2), Decimal(2), Decimal(2)
        )
        table_001.no_borders()
        return table_001

    def _build_billing_and_shipping_information(self):
        table_001 = Table(number_of_rows=6, number_of_columns=1)
        table_001.add(Paragraph("BILL TO:", font="Helvetica-Bold"))
        table_001.add(Paragraph(self.config["bill_to_name"]))
        table_001.add(Paragraph(self.config["bill_to_company"]))
        table_001.add(Paragraph(self.config["bill_to_address"]))
        table_001.add(Paragraph(self.config["bill_to_city"]))
        table_001.add(Paragraph(self.config["bill_to_postcode"]))
        table_001.set_padding_on_all_cells(
            Decimal(2), Decimal(2), Decimal(2), Decimal(2)
        )
        table_001.no_borders()
        return table_001

    def _build_itemized_description_table(self):
        table_001 = Table(number_of_rows=7, number_of_columns=2)

        table_001.add(
            TableCell(
                Paragraph("DESCRIPTION"),
                background_color=HexColor("e8e7e3"),
            )
        )
        table_001.add(
            TableCell(
                Paragraph("AMOUNT", horizontal_alignment=Alignment.RIGHT),
                background_color=HexColor("e8e7e3"),
            )
        )

        even_color = HexColor("ffffff")

        table_001.add(
            TableCell(
                Paragraph(self.config["description"]),
                background_color=even_color,
                border_bottom=False,
            )
        )
        table_001.add(
            TableCell(
                Paragraph(
                    f"£{self.config['amount']}", horizontal_alignment=Alignment.RIGHT
                ),
                background_color=even_color,
                border_bottom=False,
            )
        )

        # Optionally add some empty rowsfor styling purposes
        for _ in range(0, 8):
            table_001.add(
                TableCell(
                    Paragraph(" "),
                    background_color=even_color,
                    border_top=False,
                    border_bottom=False,
                )
            )

        table_001.add(
            TableCell(
                Paragraph(
                    "Total", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT
                ),
                border_bottom=False,
                border_left=False,
            )
        )
        table_001.add(
            TableCell(
                Paragraph(
                    f"£{self.config['amount']}", horizontal_alignment=Alignment.RIGHT
                ),
                background_color=HexColor("e8e7e3"),
            )
        )

        table_001.set_padding_on_all_cells(
            Decimal(2), Decimal(2), Decimal(2), Decimal(2)
        )
        return table_001

    def _build_payment_information(self):
        table_001 = Table(number_of_rows=4, number_of_columns=1)
        table_001.add(Paragraph("Payment details:", font="Helvetica-Bold"))
        table_001.add(Paragraph(self.config["payment_name"]))
        table_001.add(Paragraph(f"Account: {self.config['payment_account']}"))
        table_001.add(Paragraph(f"Sort code: {self.config['payment_sortcode']}"))
        table_001.set_padding_on_all_cells(
            Decimal(2), Decimal(2), Decimal(2), Decimal(2)
        )
        table_001.no_borders()
        return table_001


def get_config(config_path, inv_type):
    config = configparser.ConfigParser()
    config.read(config_path)
    if inv_type is not None:
        if inv_type not in config:
            raise click.ClickException(
                f"Invalid invoice type '{inv_type}' (config file {config_path}); "
                f"options are {', '.join(config.sections())}"
            )

        return {**config["DEFAULT"], **config[inv_type]}
    else:
        return config["DEFAULT"]


def validate_config_exists(ctx, param, value):
    if value.exists():
        return value
    raise click.BadParameter(f"Config file {value} does not exist")


def validate_dates(ctx, param, dates):
    python_dates = []
    errors = []
    for date in dates:
        try:
            python_dates.append(datetime.strptime(date, "%Y%m%d"))
        except ValueError as e:
            errors.append(f"   '{date}': {e}")
    if errors:
        errors_str = "\n".join(errors)
        raise click.BadParameter(f"\n{errors_str}")
    return sorted(python_dates)


@click.command()
@click.option(
    "--config",
    "-c",
    default="config.ini",
    type=Path,
    help="Location of config file; defaults to 'config.ini' in current directory",
    callback=validate_config_exists,
)
@click.option(
    "--invoice-type",
    "-t",
    help="Invoice type; must correspond to a section in config.ini",
)
@click.option(
    "--invoice-num",
    "-i",
    type=int,
    default=1,
    help="Invoice number to start at; defaults to 1",
)
@click.option(
    "--dates",
    "-d",
    required=True,
    multiple=True,
    callback=validate_dates,
    help="Invoice dates, in YYYYMMDD format",
)
def generate_invoices(config, invoice_type, invoice_num, dates):
    generator = InvoiceGenerator(get_config(config, invoice_type))
    for date in dates:
        generator.generate(date, invoice_num)
        invoice_num += 1


if __name__ == "__main__":
    generate_invoices()
