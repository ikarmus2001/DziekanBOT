# DziekanBot

Studiowanie w czasie pandemii zmusiło nas niemalże wyłącznie do komunikacji internetowej.
W tym celu utworzyliśmy kierunkowy serwer na platformie Discord, gdzie podzieliliśmy się na kanały zgodnie z naszymi przydziałami do grup.

Dla administratorów serwera (którym również miałem przyjemność być) oznaczało to dużo pracy, ponieważ co semestr należało usunąć każdemu z użytkowników rangę
(która umożliwiała dostęp wyłącznie do kanałów odpowiadających grupom, do których osoba uczęszczała - pomagało to zapobiec dezinformacji w zakresie pracy, terminach spotkań itp).

Aby zautomatyzować ten proces, napisaliśmy DzikanBOTa - komputerowego administratora, który po wywołaniu odpowiednich komend odznaczał koniec semestru, usuwał rangi użytkownikom (wcześnej wykonując backup),
a następnie przywracał do życia kanał rejestracyjny, w którym prostą komendą każdy z użytkowników mógł zadeklarować się do której z grup na jakim przedmiocie uczęszcza.

Bot niemalże na pewno nie będzie działał w obecnym stanie ze względu na krytyczne zmiany w zachowaniu API Discorda :(
