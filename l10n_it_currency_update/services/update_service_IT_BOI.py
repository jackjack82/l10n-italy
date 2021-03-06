# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso, Gabriele Baldessari
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.currency_rate_update import CurrencyGetterInterface

import csv
from StringIO import StringIO
import urllib2

from odoo import _
from odoo.exceptions import except_orm


class IT_BOIGetter(CurrencyGetterInterface):
    """Implementation of Curreny_getter_factory interface
    for Bank of Italy
    """
    # Bank of Italy provides a web service to access the exchange rate
    # http://www.bancaditalia.it/compiti/operazioni-cambi/cambi-automatici.pdf
    code = 'IT_BOI'
    name = 'Bank of Italy - rates'

    supported_currency_array = [
        "AFN", "ALL", "DZD", "ADP", "AOA", "XCD", "ANG", "SAR", "ARS", "AMD",
        "AWG", "AUD", "ATS", "AZN", "AZM", "BSD", "BHD", "BDT", "BBD", "BEF",
        "BZD", "XOF", "BMD", "BTN", "BYB", "BYN", "BYR", "BOB", "BAM", "BWP",
        "BRL", "BND", "BGL", "BGN", "XOF", "BIF", "KHR", "XAF", "CAD", "CVE",
        "KYD", "CZK", "CSK", "XAF", "XAF", "CLP", "CNY", "CYP", "COP", "KMF",
        "XAF", "ZRN", "CDF", "KPW", "KRW", "XOF", "CRC", "HRK", "CUP", "DKK",
        "XCD", "DOP", "ECS", "EGP", "SVC", "AED", "ERN", "EEK", "ETB", "FKP",
        "FJD", "PHP", "FIM", "XDR", "FRF", "XAF", "GMD", "GEL", "DEM", "DDM",
        "GHS", "GHC", "JMD", "JPY", "GIP", "DJF", "JOD", "GRD", "XCD", "GTQ",
        "GNF", "GWP", "XOF", "XAF", "GQE", "GYD", "HTG", "HNL", "HKD", "INR",
        "IDR", "IRR", "IQD", "IEP", "ISK", "ILS", "ITL", "YUM", "KZT", "KES",
        "KGS", "KWD", "LAK", "LSL", "LVL", "LBP", "LRD", "LYD", "LTL", "LUF",
        "MOP", "MKD", "MGA", "MGF", "MWK", "MYR", "MVR", "XOF", "MLF", "MTL",
        "MAD", "MRO", "MUR", "MXN", "MDL", "MNT", "MZM", "MZN", "MMK", "NAD",
        "NPR", "NIO", "XOF", "NGN", "NOK", "NZD", "NLG", "OMR", "PKR", "PAB",
        "PGK", "PYG", "PEN", "XPF", "PLN", "PTE", "QAR", "GBP", "ROL", "RON",
        "RUB", "RWF", "SBD", "WST", "SHP", "STD", "XOF", "CSD", "RSD", "CSD",
        "SCR", "SLL", "SGD", "SYP", "ECU", "SKK", "SIT", "SOS", "ESP", "LKR",
        "XCD", "XCD", "USD", "XCD", "ZAR", "SSP", "SDG", "SDD", "SRG", "SRD",
        "SEK", "CHF", "SZL", "TJS", "TJR", "TWD", "TZS", "THB", "XOF", "TOP",
        "TTD", "TND", "TRY", "TRL", "TMM", "TMT", "UAH", "UGX", "HUF", "EUR",
        "SUR", "UYU", "UZS", "VUV", "VEF", "VEB", "VND", "YER", "YDD", "ZMW",
        "ZMK", "ZWD", "ZWN", ]

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days, ref_date):
        """
        Implementation of abstract method of Curreny_getter_interface.
        For technical details refer to the documentation at this url:
        http://www.bancaditalia.it/compiti/operazioni-cambi/cambi-automatici.pdf
        """
        # Emptying the dictionary of currencies to update
        self.updated_currency = {}
        # We do not want to update the main currency
        if main_currency in currency_array:
            currency_array.remove(main_currency)

        url = (
            "http://cambi.bancaditalia.it/cambi/QueryOneDateAllCur?"
            "lang={lang}&rate={rate}&initDay={day}&initMonth={month}"
            "&initYear={year}&refCur={ref_cur}&R1=csv".format(
                lang='ita',
                rate='0',
                day=ref_date.day,
                month=ref_date.month,
                year=ref_date.year,
                ref_cur='euro',
                ))
        response = urllib2.urlopen(url).read()
        filename = StringIO(response)
        output_csv = csv.reader(filename, delimiter=',')
        # check that the file has no error, i.e. more than 1 line
        row_count = sum(1 for line in output_csv)
        if row_count > 1:
            filename.seek(0)
            output_csv = csv.reader(filename, delimiter=',')
            for row in output_csv:
                if len(row) > 2:
                    curr = row[2]
                    value = row[4]
                    if curr in currency_array:
                        self.updated_currency[curr] = value

        return self.updated_currency, self.log_info, ref_date
