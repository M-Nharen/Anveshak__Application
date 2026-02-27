V_Table = [[[0.0 for p in range(2)] for f in range(21)] for n in range(6)]

#This table has all the states and can be accessed as V_Table[n][F][p] for p 0:slow 1:fast

for n in range(1,6):
    for F in range(10):
        for p in range(2):
            if F<=7:
                Qslow = 5+0.8*V_Table[n-1][F+1][0]+0.2*V_Table[n-1][F+2][0]
            elif F == 8:
                Qslow = -16+0.8*V_Table[n-1][F+1][0]
            elif F == 9:
                Qslow = -100
            
            if p == 0:
                if F <= 5:
                    Qfast = 8+0.7*V_Table[n-1][F+3][1]+0.3*V_Table[n-1][F+4][1]
                elif F == 6:
                    Qfast = -24.4 +0.7*V_Table[n-1][F+3][1]
                else:
                    Qfast = -100
            else:
                if F <= 2:
                    Qfast = 8+0.6*V_Table[n-1][F+5][1]+0.4*V_Table[n-1][F+7][1]
                elif F <= 4:
                    Qfast = -35.2+0.6*V_Table[n-1][F+5][1]
                else:
                    Qfast = -100
            
            V_Table[n][F][p] = max(Qslow,Qfast)

print(V_Table[5])