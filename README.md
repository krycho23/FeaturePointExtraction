*To jest część kodu do mojej pracy magisterskiej. 
Został zaprezentowany algorytm sncc oraz tworzenie mapy błędów, histogramów i wykresów z wyników miar bad0.5, bad2.0, bad4.0. Do projektu używałem systemu Linux Ubuntu 16.04.*

Za pomocą plików wykonywalnych wygenerowanych z plików sad.cpp, ssd.cpp oraz sncc.cpp stworzono mapy dysparycji dla algorytmów SAD, SSD oraz SNCC [19]. Fragment implementacji dla pliku sncc.cpp znajduję się poniżej. Plik sncc.cpp jest autorstwa Matteo Bustreo z jego repozytorium o nazwie dispev :


 
		Rys.12 Fragment implementacji dla algorytmu SNCC
Program ten przyjmuje jako parametr maksymalną wartość dysparycji, minimalną wartość dysparycji, wielkość okna filtrującego oraz wielkość okna sumującego. Program ten jest zoptymalizowany na szybkie wyznaczanie map dysparycji, ponieważ nie przechodzi on pętlą po wszystkich wartościach pikseli, tylko po wartościach dysparycji. Pętla 1.1 oraz 1.2 są wykonane na macierzach pierwsza z nich wylicza miarę, druga ją agreguje. Po jednym przejściu pętli powstaje macierz z nowymi wartościami dysparycji. 
Mapy dysparycji, których maksymalna wartość nie przekraczała 255 przechowywano jako obraz z rozszerzeniem png. Ponieważ  nie udało się utworzyć prawidłowo 16 bitowych map dysparycji w formacie png w języku C++ dla tych obrazów dla których ta wartość była większa niż 255 oprócz wizualizacji za pomocą pliku z rozszerzeniem png (minimalnie stratnej), utworzono także pliki z danymi w formacie yml [20], które pozwoliły na bezstratne przechowywanie danych. Pliki napisane w języku python przez autora tej pracy magisterskiej: 1stage_executor.py oraz 2stage_executor.py seryjnie uruchamiały programy wykonywalne dla algorytmów dla różnych wielkości okien. Przykładowych kod poniżej:
 
		Rys.13 Fragment pliku automatyzującego wykonywanie algorytmów 			wyznaczania dysparycji
Następnie mapy dysparycji porównywano z ground-truth. Wyniki dla różnych miar przechowywano w plikach txt. Przykładowa nazwa takiego pliku znajdującego się w folderze errormeasures to my_matching.txt. Następnie odczytywano konkretne wartości miar za pomocą regexa. W dalszej kolejności tworzono wykresy, histogramy, mapy błędów.
 
		Rys.14 Funkcja obliczająca miarę bad dla punktów 					charakterystycznych
Powyżej przedstawiono funkcję obliczającą miarę bad dla punktów charakterystycznych , przyjmuje ona błędy dla punktów charakterystycznych za pomocą parametru sparse_list, argument delta określa czy będzie to miara bad0.5, bad2.0 czy też inna. Funkcja ta jest jedną z funkcji klasy MyMatching z pliku mymatching.py napisanego przez autora tej pracy magisterskiej. Klasa ta tworzy wyżej wymienione histogramy oraz mapy błędów. Do ich tworzenia wykorzystano bibliotekę matplotlib. Za pomocą programu z pliku matchfactorvisualisation.py stworzono także z użyciem biblioteki matplotlib wykresy punktowe. Dodatkowo wyniki dla poszczególnych algorytmów w zależności od okna przechowywano w  uporządkowanych słownikach (ang. ordered dictionaries). Za pomocą programu z pliku plots_myimagebad2.0.py tworzono tabele z użyciem biblioteki plotly. 
Poniżej przedstawiono funkcję, która pozwalała weryfikować czy poprawnie oceniono na podstawie wykresu najlepsze okno dla danego algorytmu:
 
		Rys.15 Funkcja znajdująca najlepsze okno dla algorytmuWyszukuje on najmniejszą wartość dla miary i znajduje odpowiadające mu okno. 
Do kalibracji użyto pliku stereo_calib.cpp z repozytorium Opencv. Ścieżki do plików z szachownicą były podawane w pliku stereo_calib.xml. W wyniku otrzymywano parametry wewnętrzne oraz zewnętrzne . Parametry te zapisano odpowiednio w plikach intrinsics.yml oraz extrinsics.yml. Napisano własny plik do generowania zbioru danych z szachownicą o nazwie calibration_dataset_real_time.py. Następnie odczytywano te parametry i kalibrowano oraz usuwano zniekształcenia we właściwym obrazie z użyciem pliku stereo_calib_real.cpp. Obrazy kalibrowane oraz właściwy obraz były wykonywane dla takiego samego ustawienia kamer w przestrzeni. 
Do usuwania zniekształceń została wykorzystana funkcja initUndistortRectifyMap. 
 
	Rys.16 Fragment wywołania funkcji usuwania zniekształceń z jej 		parametrami
Parametry cameraMatrix[0], cameraMatrix[1], distCoeffs[0], distCoeffs[1] to parametry wewnętrzne. Parametry R1, R2, P1, P2 są to parametry zewnętrzne. Remap to macierz nowych wartości wykorzystywanych w następnej kolejności przez funkcję remap do stworzenia wynikowego obrazu. 
 
	Rys.17 Fragment wywołania funkcji tworzącej skalibrowany obraz  z jej 	parametrami
Pierwszy argumentem jest źródłowy obraz, drugim argumentem wynikowy, następnie podaje się wyżej wspomnianą macierz, ostatnim argumentem jest metoda interpolacji. 


	Testowano cztery implementacje algorytmów wyznaczania dysparycji w obrazach stereoskopowych, tymi implementacjami są metody SAD   ,SSD, a także metody SNCC oraz SGBM. Każdą metodę testowano dla różnych okien w obrębie, których wykonywano sumowanie miary tj. 11x11, 21x21, 31x31, 51x51, 101x101. Pierwsze dwie metody oraz SGBM używają jednego okna. W metodzie SNCC algorytm polega na liczeniu miary dla innego okna, a innego dla sumowania miar. Testy przeprowadzono dla 29 obrazów, w tym dla 15 obrazów treningowych oraz 13 obrazów dodatkowych dla zestawu zdjęć stereo ze strony Middleburry z roku 2014 oraz 1 zdjęcia wykonanego za pomocą własnego zestawu stereorig. Zastosowano post-processing , w celu poprawienia wyników korelacji obrazów. W ramach  post-processingu wykonano dodatkową filtrację, wykorzystano filtr używający mediany, w celu usunięcia szumów typu sól-i-pieprz, czyli takich wartości, które bardzo wykraczają poza inne, które się pojawiają w danym  regionie.  
	Jak już wcześniej wspomniano w części teoretycznej miara bad2.0 jest miarą, która podaje procent pikseli, których różnica dysparycji z wartością ground-truth o tych samych współrzędnych przekracza 2 piksele dla pełnowymiarowego obrazu  o rozdzielczości 2964x1988. Dla obrazów o mniejszych rozdzielczościach jest wprost proporcjonalnie skalowana. Wśród miar bad wartość 2 pikseli stosowana na stronie Middleburry jest wartością najczęściej stosowaną w literaturze. Stosowane są także bad0.5 oraz bad4.0 [13][23]. 

Poniżej przedstawiono wzory dla miar bad, mae oraz rmse. We wzorach z_DM odpowiada obliczonej głębokości dla mapy dysparycji, a z_ odpowiada głębokości dla ground-truth.

Dla danego piksela, gdzie i to numer piksela.
		badN:z_DM (x_i,y_i )-z_ (x_i,y_i )>N			(11)
Zliczana jest ilość pikseli które spełniają powyższy warunek, gdzie N jest wartością ze zbioru {0.5, 1, 2, 4}.  Następnie wartość jest przedstawiana w procentach.

		mae=(∑_(i,j=0)^(n,m)▒〖z_DM (x_i,y_j )-z_ (x_i,y_j )∨〗)/n				(12)
		rmse=√((∑_(i,j=0)^(n,m)▒(z_DM (x_i,y_j )-z_ (x_i,y_j ))^2 )/n)				(13)
			
Miary mae [16]oraz rmse  [17], także są wykorzystywane w  [13][23] . Miara mae to  podzielony przez ilość pikseli wynik z sumy błędów, uzyskana wartość jest wyrażona w pikselach. Miara rmse to spierwiastkowany oraz podzielony przez ilość pikseli wynik z kwadratu sumy błędów.

W pierwszej kolejności przeprowadzono testy dla miary bad2.0 liczonej dla wszystkich punktów. 
Rozpoczęto od przetestowania obrazu Motorcycle . 

 
Rys.18 Wartość miary bad2.0 w zależności od wielkości okna dla trzech metod SAD,  SSD oraz SGBM
 
Rys.19 Wartość miary bad2.0 w zależności od wielkości okna filtrującego dla metody SNCC. Wielkość okna sumującego stała (podana w legendzie).  

 
Rys.20 Wartość miary bad2.0 w zależności od wielkości okna sumującego dla metody SNCC. Wielkość okna filtrującego stała (podana w legendzie).  

Należy podkreślić, że im mniejsza wartość tym lepszy wynik. Porównanie SAD, SSD oraz SGBM na pierwszym z powyższych wykresów pokazało, że dla małego okna metoda SAD jest najlepsza z tej trójki, z kolei wraz ze zwiększaniem okna metoda SSD zaczyna dominować swoimi wynikami nad SAD oraz SGBM. Metoda SNCC z wartością okna filtrującego 11x11 oraz sumującego 31x31 jest biorąc pod uwagę wszystkie wyniki dla tego obrazu najlepszym rozwiązaniem, ponieważ osiąga ona wartość znacząco poniżej 30 procent. 

Innym obrazem testowanym był obraz Pipes.
 
Rys.21 Wartość miary bad2.0 w zależności od wielkości okna dla trzech metod SAD, SSD oraz SGBM
 
Rys.22 Wartość miary bad2.0 w zależności od wielkości okna filtrującego dla metody SNCC. Wielkość okna sumującego stała (podana w legendzie). 

 
Rys.23 Wartość miary bad2.0 w zależności od wielkości okna sumującego dla metody SNCC. Wielkość okna filtrującego stała (podana w legendzie). 

 Dla tego przypadku dla małych okien metoda SGBM okazała się lepsza niż SAD oraz SSD wraz z zwiększaniem wielkości okna wyniki dla metod SAD oraz SSD przewyższyły wyniki dla metody SGBM. Spośród tych 3 metod najlepszą okazała się SAD dla okna 31x31 osiągając rezultat nieznacznie poniżej 40 procent. Metoda SNCC wykazała się najlepszymi wynikami nawet poniżej 35 procent dla okna filtrującego 11x11, a sumującego 51x51.

Następnie przeprowadzono testy dla tytułowych punktów charakterystycznych   (ang. sparse) dla tych samych algorytmów dla obrazów Motorcycle oraz Pipes. Porównywano wyniki miar, jak i porównywano uzyskane wyniki do wyników uzyskanych dla wszystkich punktów.
 
Rys.24 Wartość miary bad2.0 w zależności od wielkości okna dla dwóch metod SAD , SSD oraz SGBM dla punktów charakterystycznych

 
Rys.25 Wartość miary bad2.0 w zależności od wielkości okna filtrującego dla metody SNCC dla punktów charakterystycznych. Wielkość okna sumującego stała (podana w legendzie). 
 

Rys.26 Wartość miary bad2.0 w zależności od wielkości okna sumującego dla metody SNCC dla punktów charakterystycznych. Wielkość okna filtrującego stała (podana w legendzie). 

Wyniki dla algorytmów SAD, SSD oraz SGBM są niemal identyczne jak z wynikami testów dla wszystkich punktów. Szczególnie niewielkimi różnicami wyróżniły się metody SAD oraz SSD co pokazano w poniższej tabeli:
 Tab.1 Wartość miary bad2.0 dla algorytmów SAD oraz SDD. Porównanie wyników dla wszystkich punktów oraz dla punktów charakterystycznych

Różnice w wynikach dla metod SAD oraz SSD nie przekraczają 1 procenta. 
Podsumowując powyższe wykresy spośród 4 metod najlepsza była metoda SNCC ponieważ uzyskała wynik na poziomie około 25 procent dla okna filtrującego 11 oraz okna sumującego 31.


 
Rys.27 Wartość miary bad2.0 w zależności od wielkości okna dla trzech metod metod SAD, SSD oraz SGBM dla punktów charakterystycznych

 
Rys.28 Wartość miary bad2.0 w zależności od wielkości okna filtrującego dla metody SNCC dla punktów charakterystycznych. Wielkość okna sumującego stała (podana w legendzie). 

 
Rys.29 Wartość miary bad2.0 w zależności od wielkości okna sumującego dla metody SNCC dla punktów charakterystycznych. Wielkość okna filtrującego stała (podana w legendzie). 

Dla małego okna 11x11 metoda SGBM jest najlepsza z trójki SGBM, SSD oraz SAD, co pokrywa się z sytuacją dla porównywania wszystkich punktów. Dla dużego okna 101x101 podczas porównania dla wszystkich punktów metoda SAD była minimalnie lepsza od SSD, dla punktów charakterystycznych jest odwrotnie. Dla dużych okien SGBM nie może konkurować z SAD oraz SSD. Metoda SNCC najlepszy wynik osiągnęła dla okna filtrującego 11 i okna sumującego 51 schodząc poniżej 35 procent co jest wynikiem wręcz identycznym jak dla porównania, w którym wzięto pod uwagę wszystkie punkty.

Dla najlepszy wyników dla poszczególnych obrazów wykonano mapy dysparycji, mapy błędów, w których zielone punkty oznaczają poprawny wynik nie przekraczający 2 pikseli, żółtym oznaczono punkty, które wyszły poza zakres 2 pikseli ale nie powyżej 10 pikseli, czerwonym oznaczono punkty, w których pomylono się znacząco to znaczy powyżej 10 pikseli. Dodatkowo wykonano także histogramy dla tych punktów obejmujące tylko punkty charakterystyczne. Poniżej zaprezentowano mapy dysparycji, mapy błędów oraz histogramy dla 4 obrazów treningowych ze zbioru danych z strony Middleburry z roku 2014.

Dla Motorcycle najlepsza okazała się miara SNCC z oknem filtrującym 11 i sumującym 31.
 
Rys.30 Mapa dysparycji

 
Rys.31 Mapa błędów

 
Rys.32 Histogram  dla mapy błędów  dla punktów charakterystycznych

Dla Adirondack najlepsza okazała się miara SNCC z oknem filtrującym 21 i sumującym 21.
 
Rys.33 Mapa dysparycji
 
 Rys.34 Mapa błędów
 
 Rys.35 Histogram dla mapy błędów dla punktów charakterystycznych


Dla Piano najlepsza okazała się miara SNCC z oknem filtrującym 11 i sumującym 31.
 
Rys.36 Mapa dysparycji
 
Rys.37 Mapa błędów

 
Rys.38 Histogram dla mapy błędów dla punktów charakterystycznych

Dla Pipes najepsza okazała się miara SNCC z oknem filtrującym 11 i sumującym 51.
 
Rys.39 Mapa dysparycji
 
 Rys.40 Mapa błędów
 
 Rys.41 Histogram dla mapy błędów dla punktów charakterystycznych

Powyższe mapy dysparycji, mapy błędów oraz histogramy potwierdzają wyniki, które zostały opisane dla najlepszych wyników dla wykresów punktowych.

Następnie zebrano wyniki w tabelę dla miary bad2.0 dla 15 obrazów z zestawu treningowego oraz 13 obrazów z zestawu dodatkowego. 


 
	Tab.2 Wartości miary bad2.0 [%] dla zestawu treningowego Middlebury z roku 2014

	 
	Tab.3 Wartości miary bad2.0 [%] dla zestawu treningowego Middlebury z roku 2014  

Na powyższych dwóch tabelach zaprezentowano wyniki dla algorytmów wyznaczania dysparycji dla zestawu treningowego ze strony Middlebury z roku 2014. Porównano 4 metody przetestowane przez autora tej pracy magisterskiej tj. SAD, SSD, SGBM, SNCC wraz z wynikami metod, które są dostępne na stronie Middlebury tj. SGBM w dwóch wariantach SGBM1 i SGBM2 oraz SNCC . Algorytmy wybrane ze strony Middlebury odpowiadają metodom SGBM oraz SNCC przetestowanym przez autora tej pracy i to właśnie ten czynnik zadecydował o umieszczeniu ich w tym porównaniu.   Z tych 15 zdjęć dla poszczególnych algorytmów zostaje obliczona średnia ważona i wyniki są zaprezentowane w kolumnie „Avg”. Dla 5 obrazów tj. PianoL, Playroom, Playtable, Shelves oraz Vintage waga w liczonej średniej wynosiła 4 procent dla reszty obrazów było to 8 procent. Zdecydowano się na taki sposób liczenia średniej ze względu na to że właśnie tak obliczono średnią na stronie ewaluacyjnej algorytmów stereo Middlebury. Zauważono, że testowany algorytm SNCC średnio o około 11 procent jest gorszy od wyników zaprezentowanych na stronie udostępniającej zestaw danych.  Jest to spowodowane tym, że w rozwiązaniach na stronie Middlebury oprócz filtru medianowego zostały zastosowane inne metody post-processingu.
  
	Tab.4 Wartości miary bad2.0 [%] dla zestawu dodatkowego Middlebury z roku 2014
 
	
Tab.5 Wartości miary bad2.0 [%] dla zestawu dodatkowego Middlebury z roku 2014

Testy przeprowadzone na zestawie dodatkowym potwierdziły tezę, że spośród 4 algorytmów SAD, SSD, SGBM oraz SNCC najlepszym jest SNCC. Jeżeli chodzi o wyniki reszty metod wyznaczania dysparycji to zauważono, że wyniki są porównywalne. Warte odnotowania jest to, że dla tego zestawu algorytm SGBM osiągnął lepsze wyniki wygrywając w tym zestawieniu z metodą SSD.

Dla metod SAD, SSD oraz SNCC oraz 4 obrazów tj. Motorcycle, Adirondack, Piano, Pipes wyznaczono najlepszą wartość okna. Następnie porównano najlepsze wyniki algorytmów nie tylko według miary bad2.0, ale także bad0.5, bad4.0, mae oraz rmse. 


Dla obrazu Motorcycle najlepszym oknem dla algorytmu SAD okazały się wartości 31x31. Dla algorytmu SSD było to okno 101x101, a dla SNCC okno filtrujące 11x11, a sumujące 31x31. Wyniki zostały zaprezentowane w poniższej tabeli:
 
 Tab.6  Porównanie algorytmów dla różnych miar dla obrazu Motorcycle

Dla każdej z miar najlepszym okazał się algorytm SNCC. Algorytm SAD okazał się lepszy od SSD dla miary bad0.5, mae oraz rmse, a gorszy dla bad2.0 oraz bad4.0.

Dla obrazu Adirondack najlepszym oknem dla algorytmu SAD oraz SSD okazało się to największe o wielkości 101x101. Dla algorytmu SNCC było to okno filtrujące 21x21 oraz sumujące 51x51. Wyniki zostały zaprezentowane w poniższej tabeli:
 
Tab.7 Porównanie algorytmów dla różnych miar dla obrazu Adirondack

Dlatego obrazu także najlepszymi wynikami dla wszystkich miar wyróżnił się algorytm SNCC, przegrywając z algorytmem SSD tylko dla miary mae. Algorytm SAD był lepszy od SSD dla miar bad0.5, bad2.0 oraz rmse , okazał się minimalnie gorszy dla bad4.0 i zdecydowanie gorszy dla miary mae. 
Dla obrazu Piano najlepszym oknem dla algorytmu SAD zostało 31x31, dla algorytmu SSD 51x51, a dla SNCC okno filtrujące 11x11 oraz okno sumujące 51x51. Wyniki zostały zaprezentowane w poniższej tabeli:

 
Tab.8 Porównanie algorytmów dla różnych miar dla obrazu Piano

Dla tego obrazu również bezkonkurencyjny był algorytm SNCC przewyższając znacząco we wszystkich miarach algorytmu SAD oraz SSD. Należy odnotować, że jednogłośnym zwycięzcą w konfrontacji SAD oraz SSD został algorytm SAD, w tym przypadku był lepszy dla każdej miary.

Dla obrazu Pipes najlepszym oknem dla algorytmu SAD zostało 31x31, dla algorytmu SSD 101x101, a dla SNCC okno filtrujące 11x11 oraz sumujące 51x51. Wyniki zostały zaprezentowane w poniższej tabeli:
 
Tab.9 Porównanie algorytmów dla różnych miar dla obrazu Pipes

Można zauważyć, że dla tego obrazu wyniki dla miar mae oraz rmse są zdecydowanie lepsze w porównaniu z innymi obrazami. Algorytm SNCC zdecydowanie przewyższył wynikami miar inne algorytmy , drugi w kolejności najlepszych okazał się algorytm SAD. Spostrzeżono, że dla tego obrazu algorytm SAD wyraźnie zbliżył wynikami do algorytmu SNCC.

Wykonano także porównanie algorytmów dla obrazu Pipes dla różnych rozdzielczości. Zestawienie wykonano dla różnych miar. W pierwszej kolejności porównano wyniki algorytmów dla rozdzielczości o połowę mniejszej 1482x994.

 

Tab.11 Porównanie algorytmów dla różnych miar dla obrazu Pipes dla rozdzielczości zmniejszonej o połowę

Spostrzeżono, że relacje między wynikami algorytmów zostały zachowane w taki sam sposób jak dla pełnej rozdzielczości tj. algorytm SNCC jest najlepszy, a drugie miejsce w tym zestawieniu zajmuje metoda SAD. Zauważono także, że w porównaniu z rezultatami dla pełnej rozdzielczości wyniki dla miar bad są średnio od 0.5 do 1 procenta gorsze.

Następnie porównano wyniki algorytmów dla rozdzielczości równej jednej czwartej z pełnej rozdzielczości tj. 741x497.

 
Tab.12 Porównanie algorytmów dla różnych miar dla obrazu Pipes dla rozdzielczości równej jednej czwartej z pełnej rozdzielczości

Dla tej rozdzielczości wyniki pogorszyły się w porównaniu z rozdzielczością równą połowę z pełnej rozdzielczości. Relacje między wynikami algorytmów potwierdzają poprzednie spostrzeżenia, jedynym wyjątkiem są wyniki dla miary bad2.0, dla której metoda SAD jest najlepsza. 
Na tym etapie użyto własnego zestawu „stereorig”, w którym znajdują się dwie kamery z interfejsem UVC. Wyniki z kamer odczytywano przy pomocy biblioteki Opencv. Zestaw „stereorig” zaprezentowano poniżej:

 
Rys.42 Zdjęcie przedstawiające zestaw „stereorig”

 Wykonany obraz  został zaprezentowany poniżej :
  
Rys.43 Wykonany obraz

Obraz został wykonany poprzez naklejenie wzorzystych kartek na okładki książek. Najwyżej położona kartka została naklejona na ścianę i znajduję się najdalej od kamery.  Obraz został skalibrowany  oraz zostały usunięte zniekształcenia. Do kalibracji kamer użyto wzoru szachownicy [18]. Wykonano ponad 30 zdjęć stereo tego wzorca. Średni błąd projekcji wyniósł 1.94, z kolei średni błąd epipolarny wyniósł 5.18 . Błędy zostały opisane w podrozdziale 1.7 . Jako wynik referencyjny posłużył najlepszy algorytm dla datasetu Middleburry, czyli SNCC z oknem filtrującym 11x11 oraz sumującym 51x51. Wynik referencyjny został także wybrany na podstawie wizualnej oceny. Ocena wizualna polegała na tym czy algorytm odpowiednio określa odległość wzorzystych kartek od kamery. Poniżej zaprezentowano wynik referencyjny:
 
Rys.44 Wynik referencyjny


Porównywano algorytm SAD, SSD oraz SNCC dla stałego okna sumującego oraz filtrującego.

Dla najlepszych okien dla powyższych algorytmów wykonano tabelę porównującą algorytmy dla różnych miar. Wyniki dla miary bad2.0 uzyskano poprzez porównanie z wynikiem referencyjnym. Testy dla metody SNCC przeprowadzono dla tego samego okna filtrującego i sumującego, tak żeby wynik referencyjny nie miał wpływu na rezultaty dla tego algorytmu.  Wykonano tabelę i przedstawiono ją poniżej: 
 
Tab.13 Porównanie algorytmów dla różnych miar dla własnego obrazu

Algorytm SAD był lepszy od SSD we wszystkich miarach. SNCC dla stałego okna wykazał się zdecydowanie lepszymi wynikami od pozostałych dwóch algorytmów.
Dla miary bad4.0 algorytm SAD zbliżył się najbardziej do SNCC osiągając wynik około 5.5 procenta, przy około 5 procentach dla SNCC.

Poniżej przedstawiono mapę błędów dla algorytmu SNCC z oknem filtrującym i sumującym 31x31, który osiągnął wynik około 6 procent dla miary bad2.0.
 
			Rys.45 Mapa błędów dla własnego obrazu
