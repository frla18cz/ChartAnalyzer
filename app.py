import streamlit as st
import yfinance as yf
import datetime
import pandas as pd
import empyrical as ep

def max_DD(sloupec):
    
    returns = data[sloupec].pct_change().dropna()

    # Výpočet maximálního drawdownu
    max_drawdown = ep.max_drawdown(returns)
    max_drawdown = f"{max_drawdown:.2%}"

    # Výpis maximálního drawdownu
    print("Maximální drawdown:", max_drawdown)
    st.markdown(f"Max_DD: ({sloupec}): **{max_drawdown}**")

            

# Aktuální datum
today = datetime.date.today()

# Datum před rokem
last_year = today - datetime.timedelta(days=365)

# Titulek aplikace
st.title('Simulace páky a úroků u reálných grafů')

# Vytvoření textových polí pro uživatelský vstup s výchozími hodnotami
ticker = st.text_input('Zadejte Ticker', 'SPY')
počáteční_kapitál_input = st.text_input('Zadejte počáteční kapitál', '10000')
roční_úroková_sazba_input = st.text_input('Zadejte roční úrokovou sazbu v procentech', '6')
leverage_input = st.text_input('Zvolte finanční páku', '1')
start_date = st.date_input('Datum od', last_year)
end_date = st.date_input('Datum do', today)

# Tlačítko pro načtení dat
if st.button('Zobrazit graf'):
    try:
        # Převod vstupních hodnot na čísla
        počáteční_kapitál = float(počáteční_kapitál_input)
        roční_úroková_sazba = float(roční_úroková_sazba_input) / 100
        leverage = float(leverage_input)

        # Načtení dat z Yahoo Finance
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("Nepodařilo se načíst data pro zadaný ticker.")
        else:
            
            # Výpočet denní úrokové sazby a hodnoty investice s úročením
            denní_úrok = (1 + roční_úroková_sazba) ** (1/252) - 1

            ###############################################################################
            #NAV_bez_úroku_bez_páky            
            ###############################################################################
            # Výpočet počtu akcií na začátku investice
            počet_akcií = počáteční_kapitál / data['Adj Close'][0]

            # Výpočet denní hodnoty investice bez úroků
            data['NAV_bez_úroku_bez_páky'] = počet_akcií * (data['Adj Close'])
            ###############################################################################



            ###############################################################################
            #NAV_bez_úroky a pákou            
            ###############################################################################
            # Výpočet počtu akcií na začátku investice
            počet_akcií = počáteční_kapitál / data['Adj Close'][0] * leverage
            print(počet_akcií)

            #expozice
            data['expozice s pákou'] = počet_akcií * (data['Adj Close'])




            # Výpočet denní hodnoty investice bez úroků
            data['NAV_bez_úroku_s_pákou'] = (počet_akcií * (data['Adj Close'])) - (počáteční_kapitál * leverage)+ počáteční_kapitál
            ###############################################################################



            ###############################################################################
            #NAV_s_úrokem_a_pákou            
            ###############################################################################
            # Inicializace seznamu pro NAV s úrokem
            nav_s_urokem = []

            # Výpočet kumulativní hodnoty investice s úrokem pro každý den
            for i in range(len(data)):
                # Výpočet kumulativního úroku pro daný den
                kumulativni_urok = (1 - denní_úrok) ** i

                hodnota_s_urokem = (počet_akcií * (data['Adj Close'][i] * kumulativni_urok)) - (počáteční_kapitál * leverage)+ počáteční_kapitál
                # hodnota_s_urokem = data['NAV_bez_úroku_s_pákou'][i] * kumulativni_urok

                nav_s_urokem.append(hodnota_s_urokem)

            # Převod seznamu na pandas Series a přiřazení k data DataFrame
            data['NAV_s_úrokem_a_pákou'] = pd.Series(nav_s_urokem, index=data.index)
            ###############################################################################










            ###############################################################################
            # Zobrazení grafů
            ###############################################################################
            st.subheader("Chart NAV")
            st.line_chart(data[['NAV_s_úrokem_a_pákou', 'NAV_bez_úroku_s_pákou', 'NAV_bez_úroku_bez_páky']])

            st.subheader("Adj Close chart")
            st.line_chart(data[['Adj Close']])
            ###############################################################################


            ###############################################################################
            # Uložení dat do CSV souboru
            ###############################################################################
            # Uložení dat do CSV souboru
            csv_file = f"{ticker}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
            csv_string = data.to_csv(index=False)

            # Tlačítko pro stažení
            st.download_button(
                label="Stáhnout data jako CSV",
                data=csv_string,
                file_name=csv_file,
                mime='text/csv',
            )
            ###############################################################################


            ###############################################################################
            # Statistiky
            ###############################################################################

            # Max DD
            benchmark_max_DD = max_DD('Adj Close')
            NAV_bez_úroku_bez_páky_max_DD = max_DD('NAV_bez_úroku_bez_páky')
            NAV_bez_úroku_s_pákou_max_DD = max_DD('NAV_bez_úroku_s_pákou')
            NAV_s_úrokem_a_pákou_max_DD = max_DD('NAV_s_úrokem_a_pákou')

            ###############################################################################

    except ValueError as e:
        st.error(f"Chyba při konverzi vstupních hodnot: {e}")
    except Exception as e:
        st.error(f"Neočekávaná chyba: {e}")