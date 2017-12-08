import simulation as sim

INI_file=sys.argv[1]
output_dir=sys.argv[2]

temperature = 1

def evol_master():
    
def evol_main_loop(tss, tts, prot, genome_size, fitness, p_inversion, p_indel):
    # making backups for the current genome
    tss_backup = tss.DataFrame.copy()
    tts_backup = tts.DataFrame.copy()
    prot_backup = prot.DataFrame.copy()
    genome_size_backup = genome_size
    fitness_backup = fitness
    
    modification = inversion(p_inversion, tss, tts, prot, genome_size)
    genome_size = indel(p_indel, tss, tts, prot, genome_size)
    if genome_size != genome_size_backup:
        modification = True
    
    # If the genome changed, we launch a simulation and compute it's fitness
    if modification:
        gene_expression = sim.start_transcribing(INI_file, output_dir, tss, tts, prot, genome_size)
        fitness = get_fitness(gene_expression, expected_profile)
        
        # if the new fitness is lower than the previous one
        # and the random choice doesn't select the new genome
        # we go back to the backups 
        if fitness < fitness_backup and np.random.rand() > np.exp((fitness-fitness_backup)/temperature):
                tss = tss_backup
                tts = tts_backup
                prot = prot_backup
                genome_size = genome_size_backup
                fitness = fitness_backup
    return (tss, tts, prot, genome_size, fitness)
                
    
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
                tss.at[i,'TSS_pos'] = min_pos + max_pos - tss['TSS_pos'][i]
                tts.at[i,'TTS_pos'] = min_pos + max_pos - tts['TTS_pos'][i]
                if tss['TUorient'][i] == '+':
                    tss.at[i,'TUorient'] = '-'
                    tts.at[i,'TUorient'] = '-'
                else:
                    tss.at[i,'TUorient'] = '+'
                    tts.at[i,'TUorient'] = '+'
        for i in range(len(prot['prot_pos'])):
            if min_pos <= prot['prot_pos'][i] and max_pos >= prot['prot_pos'][i]:
                prot.at[i,'prot_pos'] = min_pos + max_pos - prot['prot_pos'][i]
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
                tss.at[i,'TSS_pos'] += insertion
                tts.at[i,'TTS_pos'] += insertion
        deleted_prot = -1
        for i in range(len(prot['prot_pos'])):
            if pos < prot['prot_pos'][i]:
                prot.at[i,'prot_pos'] += insertion
            if pos == prot['prot_pos'][i]:
                deleted_prot = i # check if a barrier is being removed
        if deleted_prot != -1:
            prot.drop(deleted_prot)
        genome_size += insertion
    return genome_size
    
def get_fitness(gene_expression, expected_profile):
    if len(gene_expression) != len(expected_profile):
        print("Error : gene_expression and expected_profile don't have the same length : %d vs %d",len(gene_expression),len(expected_profile))
    total = sum(gene_expression)
    profile = [expression / total for expression in gene_expression]
    distance = sum([np.abs(profile[i]-expected_profile[i]) for i in range(len(profile))])
    return np.exp(-distance) # fitness is exp(-distance) so it's between 0 and 1
