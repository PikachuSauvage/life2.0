import simulation as sim

def start_evol():
    
def evol_loop(tss, tts, prot, genome_size, fitness):
    
def inversion(p_inversion, tss, tts, prot, genome_size):
    if np.random.rand() < p_inversion:
        correct_positions = False
        while not correct_positions:
            correct_positions = True
            a = np.random.randint(genome_size) + 1
            b = np.random.randint(genome_size) + 1
            for pos in [a,b]:
                for i in range(len(tss['TUindex'])): # check if a position is not inside a transcript
                    if tss['TUorient'][i] == '+':
                        if pos > tss['TSS_pos'][i] and pos < tts['TTS_pos'][i]:
                            correct_positions = False
                    else:
                        if pos < tss['TSS_pos'][i] and pos > tts['TTS_pos'][i]:
                            correct_positions = False
        min_pos = min([a,b])
        max_pos = max([a,b])
        for i in range(len(tss['TUindex'])): # change transcript's positions and orientation
            if min_pos <= tss['TSS_pos'][i] and max_pos >= tss['TSS_pos'][i]:
                tss['TSS_pos'][i] = min_pos + max_pos - tss['TSS_pos'][i]
                tts['TTS_pos'][i] = min_pos + max_pos - tts['TTS_pos'][i]
                if tss['TUorient'][i] == '+':
                    tss['TUorient'][i] == '-'
                    tts['TUorient'][i] == '-'
                else:
                    tss['TUorient'][i] == '+'
                    tts['TUorient'][i] == '+'
        for i in range(len(prot['prot_pos'])):
            if min_pos <= prot['prot_pos'][i] and max_pos >= prot['prot_pos'][i]:
                prot['prot_pos'][i] = min_pos + max_pos - prot['prot_pos'][i]
        return True # if there has been an inversion
    else:
        return False # if no changes occured
    
        
def indel(p_indel, tss, tts, prot, genome_size):
    if np.random.rand() < p_indel:
        correct_position = False
        while not correct_position:
            correct_position = True
            pos = np.random.randint(genome_size) + 1
            for i in range(len(tss['TUindex'])):
                if tss['TUorient'][i] == '+':
                    if pos >= tss['TSS_pos'][i] and pos <= tts['TTS_pos'][i]:
                        correct_position = False
                else:
                    if pos <= tss['TSS_pos'][i] and pos >= tts['TTS_pos'][i]:
                        correct_position = False
        if np.random.rand() < 0.5: # same probability for insertion or deletion
            insertion = 1
        else:
            insertion = -1
        for i in range(len(tss['TUindex'])):
            if pos < tss['TSS_pos'][i]:
                tss['TSS_pos'][i] += insertion
                tts['TTS_pos'][i] += insertion
        deleted_prot = -1
        for i in range(len(prot['prot_pos'])):
            if pos < prot['prot_pos'][i]:
                prot['prot_pos'][i] += insertion
            if pos == prot['prot_pos'][i]:
                deleted_prot = i # check if a barrier is to be removed
        if deleted_prot != -1:
            prot['prot_pos'].pop(deleted_prot)
            prot['prot_name'].pop(deleted_prot)
        genome_size += insertion
    return genome_size
    
def get_fitness(gene_expression, expected_profile):
