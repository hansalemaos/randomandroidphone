import os
import random
import re
import pandas as pd


def checksum(number, alphabet="0123456789"):
    r"""Calculate the Luhn checksum of a number.

    Args:
        number (int or str): The number for which to calculate the checksum.
        alphabet (str, optional): The alphabet used for the checksum calculation.
            Defaults to "0123456789".

    Returns:
        int: The Luhn checksum of the number.
    """
    n = len(alphabet)
    number = tuple(alphabet.index(i) for i in reversed(str(number)))
    return (sum(number[::2]) + sum(sum(divmod(i * 2, n)) for i in number[1::2])) % n


def calc_check_digit(number, alphabet="0123456789"):
    r"""Calculate the Luhn check digit for a given number.

    Args:
        number (int or str): The number for which to calculate the check digit.
        alphabet (str, optional): The alphabet used for the checksum calculation.
            Defaults to "0123456789".

    Returns:
        str: The Luhn check digit as a string.
    """
    check_digit = checksum(number + alphabet[0])
    return alphabet[-check_digit]


class RandomPhone:
    r"""Generate random phone numbers and associated data for a specific country.

    Args:
        country (str): The country for which to generate phone numbers.
        phone_format_without_country (list or tuple, optional): A list or tuple of phone number format specifications
            without the country code. Defaults to an empty list.

    Attributes:
        country (str): The country for which the phone numbers are generated.
        phone_format_without_country (list): The list of phone number format specifications without the country code.
        df (pandas.DataFrame): A DataFrame containing phone data related to TACs (Type Allocation Codes).
        df2 (pandas.DataFrame): A DataFrame containing phone data related to country codes.
    """

    def __init__(self, country: str, phone_format_without_country: list | tuple = ()):
        self.country = country
        self.phone_format_without_country = [
            [str(y) for y in x] for x in phone_format_without_country
        ]
        phone_format_without_countrytmp = [
            len(sorted(x, key=len)[-1]) for x in self.phone_format_without_country
        ]
        self.phone_format_without_country = [
            [y.zfill(phone_format_without_countrytmp[ini]) for y in x]
            for ini, x in enumerate(self.phone_format_without_country)
        ]
        f1 = os.path.join(os.sep.join(__file__.split(os.sep)[:-1]), "phoneswithtac.pkl")
        f2 = os.path.join(
            os.sep.join(__file__.split(os.sep)[:-1]), "phonecodescountry.pkl"
        )

        self.df = pd.read_pickle(f1)
        self.df2 = pd.read_pickle(f2)
        self.df2 = self.df2.loc[
            self.df2.aa_country.str.contains(
                self.country, regex=True, na=False, flags=re.I
            )
        ].copy()

    def _get_phone_number(self, phonenumber: None | str = None):
        if phonenumber:
            pass
        elif self.phone_format_without_country:
            formatedphone = []
            for chunks in self.phone_format_without_country:
                formatedphone.append(random.choice(chunks))
            phonenumber = "".join(formatedphone)
        else:
            raise ValueError(
                "Need a phone number, either a string, or a tuple/list of tuples/lists: ((11,12,3), (9.))"
            )
        phonenumber = re.sub(r"\D+", "", str(phonenumber))
        return phonenumber

    def _get_phone_data(self, phonenumber: None | str = None):
        phonenumber = self._get_phone_number(phonenumber=phonenumber)
        sa2 = self.df.sample().copy()
        tac = str(sa2.bb_tac1.iloc[0])

        sa = self.df2.sample().copy()
        imsi = str(str(sa.aa_mcc.iloc[0]) + str(sa.aa_mnc.iloc[0]) + phonenumber)[:15]

        imei = (tac + str(random.randint(0, 999999)).zfill(6))[:14]

        checknumberimei = calc_check_digit(imei, alphabet="0123456789")
        imei = imei + checknumberimei

        iccid = str(
            "89"
            + (str(sa.aa_line.iloc[0]) + "0" * 6)[:6]
            + str(sa.aa_mnc.iloc[0])
            + (str(phonenumber) + 12 * "0")[:10]
        )[:19]
        iccid += calc_check_digit(iccid)

        macaddressprefix = sa2.bb_mac_prefix.iloc[0]
        totallen = 17
        macaddressprefixlen = totallen - len(macaddressprefix)
        macaddress = (
            str(macaddressprefix)
            + (":%02x:%02x:%02x" % tuple(random.randint(0, 255) for v in range(3)))[
                -macaddressprefixlen:
            ]
        ).upper()
        sa2 = sa2.assign(
            cc_imsi=imsi,
            cc_imei=imei,
            cc_iccid=iccid,
            cc_macaddress=macaddress,
            cc_phone_number=(str(sa.aa_line.iloc[0])) + phonenumber,
        ).reset_index(drop=True)
        return pd.concat([sa2, sa.reset_index(drop=True)], axis=1)

    def get_phone_data(
        self, phonenumber: None | str = None, qty: int = 1
    ) -> pd.DataFrame:
        r"""Generate multiple sets of associated data for phone numbers.

        Args:
            phonenumber (str or None, optional): A specific phone number to use. If not provided, random phone numbers
                will be generated based on the phone number format without the country code.
            qty (int, optional): The number of sets of associated data to generate. Defaults to 1.

        Returns:
            pandas.DataFrame: A DataFrame containing multiple sets of associated data for the generated phone numbers.

        Example:
            # For Brazil
            from randomandroidphone import RandomPhone
            states = [
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                21,
                22,
                24,
                27,
                28,
                31,
                32,
                33,
                34,
                35,
                37,
                38,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                51,
                53,
                54,
                55,
                61,
                62,
                63,
                64,
                65,
                66,
                67,
                68,
                69,
                71,
                73,
                74,
                75,
                77,
                79,
                81,
                82,
                83,
                84,
                85,
                86,
                87,
                88,
                89,
                91,
                92,
                93,
                94,
                95,
                96,
                97,
                98,
                99,
            ]
            cellphone = RandomPhone(
                country="Brazil",
                phone_format_without_country=(
                    states,
                    (9,),
                    list(range(0, 9999)),
                    list(range(0, 9999)),
                ),
            )
            cellphone.df = cellphone.df.loc[
                (cellphone.df.aa_android_version >= 7) & (cellphone.df.aa_android_version < 10)
            ]
            cellphone.df2 = cellphone.df2.loc[
                (cellphone.df2.aa_network.isin(["Oi", "Vivo", "TIM"]))
            ]
            da = cellphone.get_phone_data(phonenumber=None, qty=5)
            print(da)

            #   aa_brand      aa_device aa_manufacturer        aa_model_name  aa_ram_totalmem aa_form_factor   aa_system_on_chip                   aa_gpu  aa_screen_densities              aa_abis  aa_android_sdk_versions  aa_opengl_es_versions  aa_width  aa_height   bb_tac1                                        bb_model1_1        bb_model2_1  bb_total_rating  aa_android_version bb_mac_prefix          cc_imsi          cc_imei              cc_iccid      cc_macaddress cc_phone_number aa_country aa_network  aa_mcc  aa_mnc aa_line    aa_iso
            # 0   QSmart         MARK_2          Qsmart               Mark 2             1003          Phone    Mediatek MT6580M                      NaN                  240  armeabi;armeabi-v7a                       28                 131072       480        960  35440811          Digicom Trading PVT Limited QSmart Mark 2       QSmart Mark2            360.0                 9.0      00:0A:00  724112497036871  354408118779849  89550000112497036872  00:0A:00:29:F4:CA   5524970368714     Brazil       Vivo     724      11      55  BR / BRA
            # 1    iBall  Slide_Skye_03           iBall  iBall_Slide_Skye_03              948         Tablet  Spreadtrum SC7731E  ARM Mali T820 (600 MHz)                  160  armeabi;armeabi-v7a                       27                 196610       600       1024  91164695  Best IT World (India) Pvt Ltd iBall Slide Skye 03  Iball SlideSkye03            380.0                 8.1      40:45:DA  724638979578075  911646952997003  89550000638979578072  40:45:DA:8E:11:80   5538979578075     Brazil       Vivo     724       6      55  BR / BRA
            # 2     DEXP           P410            DEXP                 P410              948         Tablet  Spreadtrum SC7731E  ARM Mali T820 (600 MHz)                  213  armeabi;armeabi-v7a                       27                 196610       800       1280  35495910                              Factor LLC Ursus P410     DEXP UrsusP410            360.0                 8.1      40:45:DA  724169799721846  354959103507751  89550000169799721841  40:45:DA:42:11:26   5597997218460     Brazil         Oi     724      16      55  BR / BRA
            # 3  Maximus         Noir_X         Maximus               Noir X              927          Phone  Spreadtrum SC9832E  ARM Mali T820 (680 MHz)                  240  armeabi;armeabi-v7a                       27                 196610       480        854  35917109                Quartel Infotech Ltd Maximus Noir X      Maximus NoirX            360.0                 8.1      40:45:DA  724482984743677  359171090807716  89550000482984743672  40:45:DA:D6:AB:7E   5582984743677     Brazil        TIM     724       4      55  BR / BRA
            # 4    AMGOO          AM509           Amgoo                AM509              953          Phone     Mediatek MT6737  ARM Mali T720 (550 MHz)                  240  armeabi;armeabi-v7a                       24                 196609       480        854  35263909       Dragon-Inn Communications Co Ltd AMGOO AM509        Amgoo AM509            360.0                 7.0      00:0A:00  724263935091242  352639091601251  89550000263935091241  00:0A:00:EF:74:67   5563935091242     Brazil        TIM     724       2      55  BR / BRA

        """
        allresults = []
        while len(allresults) < qty:
            try:
                allresults.append(self._get_phone_data(phonenumber=phonenumber))
            except Exception:
                continue
        if len(allresults) == 1:
            return allresults[0]
        return pd.concat(allresults, ignore_index=True)
