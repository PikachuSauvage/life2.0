import simulation as sim

def start_evol():
    
def evol_loop(tss, tts, prot, genome_size, fitness):
    
def inversion(tss, tts, prot, genome_size):
    correct_positions = False
    while not correct_positions:
        correct_positions = True
        a = np.random.randint(genome_size)
        b = np.random.randint(genome_size)
        for pos in [a,b]:
            for i in len(tss['TUindex']):
                if tss['TUorient'][i] == '+':
                    if pos > tss['TSS_pos'][i] and pos < tts['TTS_pos'][i]:
                        correct_positions = False
                else:
                    if pos < tss['TSS_pos'][i] and pos > tts['TTS_pos'][i]:
                        correct_positions = False
    min_pos = min([a,b])
    max_pos = max([a,b])
    for i in len(tss['TUindex']):
        if min_pos <= tss['TSS_pos'][i] and max_pos >= tss['TSS_pos'][i]:
            tss['TSS_pos'][i] = min_pos + max_pos - tss['TSS_pos'][i]
            tts['TTS_pos'][i] = min_pos + max_pos - tts['TTS_pos'][i]
            if tss['TUorient'][i] == '+':
                tss['TUorient'][i] == '-'
                tts['TUorient'][i] == '-'
            else:
                tss['TUorient'][i] == '+'
                tts['TUorient'][i] == '+'
    for i in len(prot['prot_pos']):
        if min_pos <= prot['prot_pos'][i] and max_pos >= prot['prot_pos'][i]:
            prot['prot_pos'][i] = min_pos + max_pos - prot['prot_pos'][i]
    
        
def indel(tss, tts, prot, genome_size):
    
def get_fitness(gene_expression, expected_profile):
