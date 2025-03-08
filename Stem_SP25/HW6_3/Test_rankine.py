from Rankine_stem import rankine
from Steam_stem import steam

def main():
    # Cycle i: saturated vapor at p_high=8000 kPa
    cycle1 = rankine(p_low=8, p_high=8000, t_high=None, name='Cycle i (Saturated Vapor)')
    cycle1.calc_efficiency()
    cycle1.print_summary()

    # Cycle ii: superheated steam at p_high=8000 kPa
    # T1 = 1.7 * Tsat(8000kPa). Suppose Tsat ~ 295 °C => T1 ~ 501.5 °C
    Tsuper = 1.7 * 295  # approximate
    cycle2 = rankine(p_low=8, p_high=8000, t_high=Tsuper, name='Cycle ii (Superheated)')
    cycle2.calc_efficiency()
    cycle2.print_summary()

if __name__=="__main__":
    main()
