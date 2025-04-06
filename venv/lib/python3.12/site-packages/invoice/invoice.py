import aiohttp
import asyncio
from bs4 import BeautifulSoup

class Invoice:
    """中華民國統一發票中獎發票查詢（當期與上期）"""
    def __init__(self) -> None:
        """
        中華民國財政部統一發票中獎發票查詢（當期與上期）

        Parameters 參數
        ----------
        None：無

        Examples 範例
        --------
        >>> from invoice import Invoice
        >>> invoice = Invoice()
        >>> invoice.get_years_and_months()
        '111年05-06月'
        >>> invoice.get_numbers()
        [['特別獎', '46438476'],
        ['特獎', '54769852'],
        ['頭獎', '17858097'],
        ...
        """
        self.__soup__ = None
        self.__previous_soup__ = None
        asyncio.run(self.__run_task__())

    async def __run_task__(self) -> None:
        """
        非同步fetch網頁內容

        Parameters 參數
        ----------
        None：無

        Response 回傳
        ----------
        None：無
        """
        tasks = [
            self.__fetch_data__(),
            self.__fetch_previous_period_data__()
        ]
        await asyncio.gather(*tasks)

    async def __fetch_data__(self) -> None:
        """
        非同步fetch網頁內容

        Parameters 參數
        ----------
        None：無

        Response 回傳
        ----------
        None：無
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://invoice.etax.nat.gov.tw/index.html', ssl=False) as response:
                response = await response.text()
                self.__soup__ = BeautifulSoup(response, "html.parser")

    async def __fetch_previous_period_data__(self) -> None:
        """
        非同步fetch網頁內容

        Parameters 參數
        ----------
        None：無

        Response 回傳
        ----------
        None：無
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://invoice.etax.nat.gov.tw/lastNumber.html', ssl=False) as response:
                response = await response.text()
                self.__previous_soup__ = BeautifulSoup(response, "html.parser")

    def get_years_and_months(self) -> str:
        """
        回傳當期中獎發票之中華民國年份與月份

        Parameters 參數
        ----------
        None：無
        """
        return self.__soup__.find('a', {'class':'etw-on', 'href':'index.html'}).text[:-5]
    
    def get_previous_years_and_months(self) -> str:
        """
        回傳上期中獎發票之中華民國年份與月份

        Parameters 參數
        ----------
        None：無
        """
        return self.__soup__.find('a', {'href':'lastNumber.html'}).text[:-5]
    
    def __get_numbers__(self, soup) -> list:
        """
        回傳中獎發票之開獎號碼

        Parameters 參數
        ----------
        soup：BeautifulSoup之解析物件，為開獎發票之網頁解析

        Return 回傳
        ----------
        list:多個獎項與發票號碼的list
        """
        tr_list = soup.find_all('tr')
        numbers_list = []
        for tr in tr_list:
            prize = tr.find('td', {'headers':'th01'})
            td = tr.find('td', {'headers':'th02'})
            if not td:
                continue

            numbers = td.find_all('p', {'class':'etw-tbiggest'})
            if not numbers:
                continue

            for number in numbers:
                numbers_list.append([prize.text.strip(), number.text.strip()])
        return numbers_list
    
    def get_numbers(self) -> list:
        """
        回傳中獎發票之開獎號碼

        Parameters 參數
        ----------
        None:無

        Return 回傳
        ----------
        list:多個獎項與發票號碼的list
        """
        return self.__get_numbers__(self.__soup__)
    
    def get_previous_numbers(self) -> list:
        """
        回傳中獎發票之開獎號碼

        Parameters 參數
        ----------
        None:無

        Return 回傳
        ----------
        list:多個獎項與發票號碼的list
        """
        return self.__get_numbers__(self.__previous_soup__)
    
    def redeem(self, invoice_list:list, numbers_list:list) -> list:
        """
        發票號碼兌獎

        Parameters 參數
        --------
        invoice_list:開獎號碼清單，可由get_numbers()獲取
        numbers_list:欲兌獎之發票號碼list

        Examples 範例
        --------
        >>> invoice = Invoice()
        >>> invoice_list = invoice.get_numbers()
        >>> my_numbers = [
            '12345678',
            '12345677',
            ...,
            '123'
        ]
        >>> prize_list = invoice.redeem(invoice_list, my_numbers)
        >>> print(prize_list)
        [
            ['12345678', None],
            ['12345677', '六獎'],
            ...,
            ['123', '格式有誤']
        ]

        Return 回傳
        --------
        list:多個發票號碼與對應之獎項的list
        對應之獎項若無中獎則回傳None
        """
        frist_prize = [number for prize, number in invoice_list if prize == '特別獎'][0]
        second_prize = [number for prize, number in invoice_list if prize == '特獎'][0]
        third_prize_list = [number for prize, number in invoice_list if prize == '頭獎']
        result_list = []
        for number in numbers_list:
            if type(number) is not str or len(number) != 8:
                result_list.append([number, '格式有誤'])
                continue

            if frist_prize == number:
                result_list.append([number, '特別獎'])
                continue
            if second_prize == number:
                result_list.append([number, '特獎'])
                continue

            reversed_number = number[::-1]
            for third_prize in third_prize_list:
                reversed_third_prize = third_prize[::-1]
                
                count_validate = 0
                for index in range(0, 8):
                    if reversed_third_prize[index] != reversed_number[index]:
                        break
                    else:
                        count_validate += 1

                if count_validate == 8:
                    result_list.append([number, '頭獎'])
                    break
                if count_validate == 7:
                    result_list.append([number, '二獎'])
                    break
                if count_validate == 6:
                    result_list.append([number, '三獎'])
                    break
                if count_validate == 5:
                    result_list.append([number, '四獎'])
                    break
                if count_validate == 4:
                    result_list.append([number, '五獎'])
                    break
                if count_validate == 3:
                    result_list.append([number, '六獎'])     
                    break 
            if count_validate < 3:
                result_list.append([number, None])
                continue   
        return result_list   